"""What Python sees for a field. Shared by pb and pyi so they agree.

This encodes pb's *current* behavior exactly, including its quirks (see the
notes on facade and flattened fields), so the stub describes what is really
bound. Changing a rule here changes both backends at once.
"""

from dataclasses import dataclass
from typing import Protocol

from clang import cindex

from ..node import FieldNode

# Facades with a dedicated pb field renderer; both always emit a setter.
SETTER_FACADES = frozenset({"pycapsule", "wrapper"})


class FieldTools(Protocol):
    """The renderer helpers the rules need (Worker provides all of them)."""

    wrapped: dict

    def is_char_ptr(self, cursor: cindex.Cursor) -> bool: ...
    def is_function_pointer(self, cursor: cindex.Cursor) -> bool: ...
    def get_base_type_name(self, type_: cindex.Type) -> str: ...
    def format_field(self, name: str) -> str: ...


def is_field_readonly(cursor: cindex.Cursor, structure_spec) -> bool:
    """pb's rule for plain fields: def_readonly vs def_readwrite."""
    if structure_spec is not None and structure_spec.readonly:
        return True
    if cursor.type.is_const_qualified():
        return True
    # C arrays can't be assigned. TODO in pb: render_const_array_field?
    return cursor.type.kind == cindex.TypeKind.CONSTANTARRAY


@dataclass(frozen=True)
class PyField:
    name: str                 # Python name
    cursor: cindex.Cursor     # the C++ member (nested member if flattened)
    readonly: bool

    @classmethod
    def from_node(cls, node: FieldNode, tools: FieldTools) -> list["PyField"]:
        """The Python attributes one field node produces (several if flattened)."""
        spec = node.parent.spec if node.parent is not None else None
        cursor = node.cursor

        if node.spec is not None and node.spec.flatten:
            return [
                cls(tools.format_field(nested.spelling), nested,
                    cls.flattened_readonly(nested, spec, tools))
                for nested in cursor.type.get_canonical().get_fields()
            ]

        if node.facade is not None and node.facade.kind in SETTER_FACADES:
            # PyCapsuleFieldRenderer / WrapperFieldRenderer ignore readonly.
            readonly = False
        else:
            # FieldRenderer.render checks readonly before any other category.
            readonly = is_field_readonly(cursor, spec)
        return [cls(node.pyname, cursor, readonly)]

    @staticmethod
    def flattened_readonly(cursor: cindex.Cursor, spec, tools: FieldTools) -> bool:
        """FieldRenderer.render_field_property's rule for nested members."""
        if tools.is_char_ptr(cursor):
            return is_field_readonly(cursor, spec)
        if tools.is_function_pointer(cursor) or cursor.is_bitfield():
            return False  # always emitted with a setter
        if tools.get_base_type_name(cursor.type) in tools.wrapped:
            return False  # always emitted with a setter
        return is_field_readonly(cursor, spec)