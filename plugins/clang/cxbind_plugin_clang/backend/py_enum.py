from dataclasses import dataclass
from typing import Callable

from clang import cindex

from ..node import EnumNode


def has_prefix(text: str, prefix: str) -> bool:
    """Whether Session.strip_prefixes would strip `prefix` from `text`.

    Same rule: the prefix must be followed by an uppercase letter or an
    underscore, so `Kind` strips from `KindSmall` but not from `Kindling`.
    """
    return (
        bool(prefix)
        and text.startswith(prefix)
        and len(text) > len(prefix)
        and (text[len(prefix)].isupper() or text[len(prefix)] == "_")
    )


@dataclass(frozen=True)
class PyConstant:
    name: str       # Python name, e.g. NO_NAV
    spelling: str   # C++ enumerator, e.g. ImGuiWindowFlags_NoNav


@dataclass(frozen=True)
class PyEnum:
    """What Python sees for an enum. Shared by pb and pyi so they agree."""

    node: EnumNode
    constants: list[PyConstant]
    scoped: bool
    # Whether .export_values() copies the constants into the enclosing scope.
    exported: bool

    @classmethod
    def from_node(
        cls,
        node: EnumNode,
        format_enum_constant: Callable[..., str],
    ) -> "PyEnum":
        cursor = node.cursor
        enumerators = [
            child for child in cursor.get_children()
            if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL
        ]

        # Prefix stripping uses the C++ enum name, so constants stay stable
        # even if the registry renames the enum.
        constants = [
            PyConstant(format_enum_constant(e.spelling, node.first_name), e.spelling)
            for e in enumerators
        ]

        scoped = cursor.is_scoped_enum()

        # Export only if no constant lost its enum-name prefix. C prefixes
        # (ImGuiWindowFlags_None, ImGuiChildFlags_None) exist to keep names
        # unique in a shared scope; exporting the stripped names (NONE) would
        # collide, and at runtime the last enum registered would win.
        # Decided per scope by EnumExportResolver (it needs every enum in the
        # scope at once). Fallback for nodes it didn't see: the simple rule.
        if node.exported is not None:
            exported = node.exported
        else:
            stripped = any(has_prefix(e.spelling, node.first_name) for e in enumerators)
            exported = not scoped and not stripped

        return cls(node=node, constants=constants, scoped=scoped, exported=exported)