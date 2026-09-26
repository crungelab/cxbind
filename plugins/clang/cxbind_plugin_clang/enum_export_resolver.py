"""Decide which unscoped enums export their constants (.export_values()).

Stripping an enum-name prefix (ImGuiWindowFlags_None -> NONE) makes nice
member names, but the prefix existed to keep names unique in a shared
scope. Exporting stripped names can collide, and at runtime the last enum
registered silently wins.

Rule, per scope (module, or the class an enum is bound in):
  - scoped enums never export;
  - unprefixed enums always export (C already made their names unique);
  - a prefix-stripped enum exports only if none of its names clash with
    another export in the same scope.

Runs in the synthesis phase: it needs every enum in a scope at once.
Records the decision on EnumNode.exported for both backends to read.
"""

from collections import Counter, defaultdict

from clang import cindex
from loguru import logger

from .node import Node, EnumNode
from .session import Session
from .backend.py_enum import has_prefix


class EnumExportResolver:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, roots: list[Node]) -> None:
        by_scope: dict[int | None, list[tuple[EnumNode, set[str], bool]]] = defaultdict(list)

        for root in roots:
            for node in root.traverse():
                if not isinstance(node, EnumNode):
                    continue
                if node.cursor.is_scoped_enum():
                    node.exported = False
                    continue
                names, stripped = self.constants(node)
                scope = node.binding.scope if node.binding is not None else None
                by_scope[id(scope) if scope is not None else None].append(
                    (node, names, stripped)
                )

        for members in by_scope.values():
            self.resolve_scope(members)

    def constants(self, node: EnumNode) -> tuple[set[str], bool]:
        enumerators = [
            c for c in node.cursor.get_children()
            if c.kind == cindex.CursorKind.ENUM_CONSTANT_DECL
        ]
        names = {
            self.session.format_enum_constant(e.spelling, node.first_name)
            for e in enumerators
        }
        stripped = any(has_prefix(e.spelling, node.first_name) for e in enumerators)
        return names, stripped

    def resolve_scope(self, members: list[tuple[EnumNode, set[str], bool]]) -> None:
        counts = Counter(name for _, names, _ in members for name in names)

        for node, names, stripped in members:
            clashes = sorted(n for n in names if counts[n] > 1)
            node.exported = not (stripped and clashes)
            if not node.exported:
                logger.debug(
                    f"{node.pyname}: not exporting; stripped names clash in scope: "
                    f"{', '.join(clashes)}"
                )

        # Unprefixed enums that still clash: C allowed it (e.g. different
        # namespaces, flattened), but at runtime the last one wins.
        exported = Counter(
            name for node, names, _ in members if node.exported for name in names
        )
        for name, count in exported.items():
            if count > 1:
                logger.warning(
                    f"exported enum constant '{name}' is defined by {count} enums "
                    f"in one scope; at runtime only the last one survives"
                )