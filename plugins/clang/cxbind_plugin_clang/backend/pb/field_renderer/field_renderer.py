from typing import Generic, TypeVar

from clang import cindex
from loguru import logger

from cxbind.facade import Facade

from ....node import FieldNode

from ...renderer_registry import PbRendererRegistry

from ..node_renderer import NodeRenderer


@PbRendererRegistry.register("field")
class FieldRenderer(NodeRenderer[FieldNode]):
    def render(self):
        node = self.node
        pyname = node.pyname
        cursor = node.cursor

        self.begin_chain()

        if node.spec.flatten:
            logger.debug(f"Flattening field: {cursor.spelling}")
            self.render_flattened_field(cursor)
            return

        field_type_name = self.get_base_type_name(cursor.type)

        # logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')

        if self.is_field_readonly(cursor):
            self.out(f'.def_readonly("{pyname}", &{node.name})')
        else:
            if self.is_char_ptr(cursor):
                # logger.debug(f"{cursor.spelling}: is char*")
                self.render_char_ptr_field(cursor, pyname)
            elif self.is_function_pointer(cursor):
                # logger.debug(f"{cursor.spelling}: is fn*")
                self.render_fn_ptr_field(cursor, pyname)
            elif field_type_name in self.wrapped:
                self.render_wrapped_field(cursor, pyname)
            elif cursor.is_bitfield():
                self.render_bitfield(cursor, pyname)
            else:
                self.out(f'.def_readwrite("{pyname}", &{node.name})')
        # self.out()

    def render_flattened_field(self, cursor: cindex.Cursor):
        """
        Expose the members of an embedded struct (e.g. `b2JointDef base`) directly on the
        enclosing bound class, as if they were declared there. Each nested member gets its
        own def_property / def_property_readonly entry reached via self.<outer>.<nested>,
        since a pointer-to-member on the outer class can't reach into an embedded struct.
        """
        outer_name = cursor.spelling
        record_type = cursor.type.get_canonical()

        for nested_cursor in record_type.get_fields():
            nested_pyname = self.format_field(nested_cursor.spelling)
            access = f"{outer_name}.{nested_cursor.spelling}"
            self.render_field_property(nested_cursor, nested_pyname, access)

    def render_field_property(self, cursor: cindex.Cursor, pyname: str, access: str):
        """
        Render a single field as a def_property/def_property_readonly pair, where `access`
        is the expression reached from `self` (e.g. "userData" or "base.userData"). Used
        for flattened fields, and dispatches to the same categories as the top-level render.
        """
        pname = self.top_node.name
        field_type_name = self.get_base_type_name(cursor.type)
        readonly = self.is_field_readonly(cursor)

        if self.is_char_ptr(cursor):
            if readonly:
                self.out(f'.def_property_readonly("{pyname}",')
                with self.out:
                    self.out(f"[](const {pname}& self)" "{" f" return self.{access};" " }")
                self.out(")")
            else:
                self.out(f'.def_property("{pyname}",')
                with self.out:
                    self.out(f"[](const {pname}& self)" "{" f" return self.{access};" " },")
                    self.out(
                        f"[]({pname}& self, const char* source)"
                        "{"
                        f" self.{access} = strdup(source);"
                        " }"
                    )
                self.out(")")
        elif self.is_function_pointer(cursor) or cursor.is_bitfield():
            typename = cursor.type.spelling
            self.out(f'.def_property("{pyname}",')
            with self.out:
                self.out(f"[]({pname}& self)" "{" f" return self.{access};" " },")
                self.out(
                    f"[]({pname}& self, {typename} source)"
                    "{"
                    f" self.{access} = source;"
                    " }"
                )
            self.out(")")
        elif field_type_name in self.wrapped:
            wrapper = self.wrapped[field_type_name].wrapper
            extra = ""
            if wrapper == "py::capsule":
                extra = f', "{field_type_name}"'
            result = f"{wrapper}(self.{access}{extra})"
            value = f"const {wrapper}& value"
            self.out(f'.def_property("{pyname}",')
            with self.out:
                self.out(f"[](const {pname}& self)" "{" f" return {result};" " },")
                self.out(f"[]({pname}& self, {value})" "{" f" self.{access} = value;" " }")
            self.out(")")
        else:
            if readonly:
                self.out(f'.def_property_readonly("{pyname}",')
                with self.out:
                    self.out(f"[](const {pname}& self)" "{" f" return self.{access};" " }")
                self.out(")")
            else:
                typename = cursor.type.get_canonical().spelling
                self.out(f'.def_property("{pyname}",')
                with self.out:
                    self.out(f"[](const {pname}& self)" "{" f" return self.{access};" " },")
                    self.out(
                        f"[]({pname}& self, {typename} value)"
                        "{"
                        f" self.{access} = value;"
                        " }"
                    )
                self.out(")")

    def render_wrapped_field(self, cursor: cindex.Cursor, pyname: str):
        pname = self.top_node.name
        name = cursor.spelling
        field_type_name = self.get_base_type_name(cursor.type)

        wrapper = self.wrapped[field_type_name].wrapper
        extra = ""
        if wrapper == "py::capsule":
            extra = f', "{field_type_name}"'
        result = f"{wrapper}(self.{name}{extra})"
        value = f"const {wrapper}& value"

        self.out("//render_wrapped_field")
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[](const {pname}& self)" "{" f" return {result};" " },")
            self.out(f"[]({pname}& self, {value})" "{" f" self.{name} = value;" " }")
        self.out(")")

    # TODO: This is creating memory leaks.  Need wrapper functionality pronto.
    def render_char_ptr_field(self, cursor: cindex.Cursor, pyname: str):
        pname = self.top_node.name
        name = cursor.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[](const {pname}& self)" "{" f" return self.{name};" " },")
            self.out(
                f"[]({pname}& self, const char* source)"
                "{"
                f" self.{name} = strdup(source);"
                " }"
            )
        self.out(")")

    def render_fn_ptr_field(self, cursor: cindex.Cursor, pyname: str):
        pname = self.top_node.name
        name = cursor.spelling
        typename = cursor.type.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[]({pname}& self)" "{" f" return self.{name};" " },")
            self.out(
                f"[]({pname}& self, {typename} source)"
                "{"
                f" self.{name} = source;"
                " }"
            )
        self.out(")")

    def render_bitfield(self, cursor: cindex.Cursor, pyname: str):
        pname = self.top_node.name
        name = cursor.spelling
        typename = cursor.type.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[]({pname}& self)" "{" f" return self.{name};" " },")
            self.out(
                f"[]({pname}& self, {typename} source)"
                "{"
                f" self.{name} = source;"
                " }"
            )
        self.out(")")

    def is_field_readonly(self, cursor: cindex.Cursor) -> bool:
        if self.top_node.spec.readonly:
            return True
        if cursor.type.is_const_qualified():
            return True
        if (
            cursor.type.kind == cindex.TypeKind.CONSTANTARRAY
        ):  # TODO: render_const_array_field?
            return True
        return False


T_Facade = TypeVar("T_Facade", bound=Facade)


class FacadeFieldRenderer(FieldRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, node: FieldNode):
        super().__init__(node)
        self.facade = node.facade