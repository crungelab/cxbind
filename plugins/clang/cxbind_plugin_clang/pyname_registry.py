"""
Two-phase Python name registry.

Build phase: builders register one PyBinding per named node via add().
Render phase: resolve() runs once, before any renderer, and assigns final
collision-free names. Renderers read node.pyname, which delegates to
node.binding.pyname.

Resolution rules, applied per (scope, pyname) group until nothing changes:
  - Same-kind functions/methods sharing a name are an overload set: allowed.
  - Instance + static methods sharing a name: every static gets "_static".
  - Anything else: every non-explicit member is qualified with its C++
    ancestors (namespaces included), one level per pass.
  - Explicit (spec-provided) names are never renamed; if they alone collide,
    resolution raises.

Nested structural types additionally carry a prefix_owner: their name is
composed from the owner's *current* pyname each pass, so a renamed owner
propagates to its nested types.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable

from clang.cindex import Cursor, CursorKind
from loguru import logger

if TYPE_CHECKING:
    from .node import Node


class BindingError(Exception):
    pass


class PyKind(Enum):
    TYPE = auto()
    FUNCTION = auto()
    METHOD = auto()
    STATIC_METHOD = auto()
    FIELD = auto()


OVERLOADABLE = frozenset({PyKind.FUNCTION, PyKind.METHOD, PyKind.STATIC_METHOD})
STATIC_SUFFIX = "_static"


@dataclass(eq=False)
class PyBinding:
    node: Node
    kind: PyKind
    scope: PyBinding | None  # owning binding; None = module. Never changes.
    base_pyname: str
    pyname: str = ""
    explicit: bool = False  # pyname fixed by a user spec
    prefix_owner: PyBinding | None = None  # naming parent; distinct from scope
    depth: int = 0  # qualifier levels applied so far

    def __post_init__(self) -> None:
        if not self.pyname:
            self.pyname = self.base_pyname


def ancestor_names(cursor: Cursor, format_type: Callable[[str], str]) -> list[str]:
    """Formatted names of semantic parents, nearest first. Includes namespaces."""
    names: list[str] = []
    c = cursor.semantic_parent
    while c is not None and c.kind != CursorKind.TRANSLATION_UNIT:
        if c.spelling:  # skip anonymous namespaces/structs
            names.append(format_type(c.spelling))
        c = c.semantic_parent
    return names


def qualified_name(cursor: Cursor | None) -> str:
    if cursor is None:
        return "<no cursor>"
    parts = [cursor.spelling]
    c = cursor.semantic_parent
    while c is not None and c.kind != CursorKind.TRANSLATION_UNIT:
        if c.spelling:
            parts.append(c.spelling)
        c = c.semantic_parent
    return "::".join(reversed(parts))


class PynameRegistry:
    def __init__(self, format_type: Callable[[str], str]) -> None:
        self.format_type = format_type
        self.bindings: list[PyBinding] = []
        self.resolved = False

    def add(
        self,
        node: Node,
        kind: PyKind,
        scope: PyBinding | None,
        base_pyname: str,
        explicit: bool = False,
    ) -> PyBinding:
        if self.resolved:
            raise BindingError(
                f"late registration after resolve: {qualified_name(node.cursor)}"
            )
        binding = PyBinding(node, kind, scope, base_pyname, explicit=explicit)
        self.bindings.append(binding)
        return binding

    def resolve(self, max_passes: int = 16) -> None:
        if self.resolved:
            return
        for _ in range(max_passes):
            if not self._resolve_once():
                self.resolved = True
                return
        raise BindingError("pyname resolution did not converge")

    # ------------------------------------------------------------------

    def _resolve_once(self) -> bool:
        changed = self._refresh_prefixes()

        groups: dict[tuple[int, str], list[PyBinding]] = defaultdict(list)
        for b in self.bindings:
            groups[(id(b.scope), b.pyname)].append(b)

        for group in groups.values():
            if self._resolve_group(group):
                changed = True
        return changed

    def _refresh_prefixes(self) -> bool:
        """Nested-type names follow their owner's current name."""
        changed = False
        for b in self.bindings:
            if b.prefix_owner is None or b.depth > 0:
                continue
            composed = b.prefix_owner.pyname + b.base_pyname
            if composed != b.pyname:
                b.pyname = composed
                changed = True
        return changed

    def _resolve_group(self, group: list[PyBinding]) -> bool:
        if len(group) < 2:
            return False

        kinds = {b.kind for b in group}

        # Same-kind functions/methods: a legitimate overload set.
        if len(kinds) == 1 and kinds <= OVERLOADABLE:
            return False

        # Static/instance mix: suffix every static, stay in the same scope.
        if kinds == {PyKind.METHOD, PyKind.STATIC_METHOD}:
            statics = [b for b in group if b.kind is PyKind.STATIC_METHOD]
            if any(b.explicit for b in statics):
                raise BindingError(
                    self._describe(group, "explicit static collides with instance method")
                )
            for b in statics:
                b.pyname = f"{b.base_pyname}{STATIC_SUFFIX}"
                logger.warning(f"Renamed static {qualified_name(b.node.cursor)} -> '{b.pyname}'")
            return True

        # Anything else: qualify every non-explicit member.
        renamable = [b for b in group if not b.explicit]
        if not renamable:
            raise BindingError(self._describe(group, "explicit names collide"))
        for b in renamable:
            new = self._qualify(b)
            if new is None:
                raise BindingError(self._describe(group, "cannot disambiguate"))
            logger.warning(f"Renamed {qualified_name(b.node.cursor)} -> '{new}'")
            b.pyname = new
        return True

    def _qualify(self, b: PyBinding) -> str | None:
        chain = ancestor_names(b.node.cursor, self.format_type)
        if b.depth >= len(chain):
            return None
        b.depth += 1
        return "".join(reversed(chain[: b.depth])) + b.base_pyname

    def _describe(self, group: list[PyBinding], why: str) -> str:
        names = ", ".join(qualified_name(b.node.cursor) for b in group)
        return f"{why}: {names} -> '{group[0].pyname}'"
