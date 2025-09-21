from clang import cindex
from loguru import logger

from ...node import FieldNode
from ... import cu

from .node_renderer import NodeRenderer


class FieldRenderer(NodeRenderer[FieldNode]):
    def render(self):
        node = self.node
        pyname = node.pyname
        cursor = node.cursor

        field_type_name = cu.get_base_type_name(cursor.type)

        #logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')
        
        self.begin_chain()

        if self.is_field_readonly(cursor):
            self.out(f'.def_readonly("{pyname}", &{node.name})')
        else:
            if self.is_char_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is char*")
                self.render_char_ptr_field(cursor, pyname)
            elif self.is_function_pointer(cursor):
                #logger.debug(f"{cursor.spelling}: is fn*")
                self.render_fn_ptr_field(cursor, pyname)
            elif field_type_name in self.wrapped:
                self.render_wrapped_field(cursor, pyname)
            else:
                self.out(f'.def_readwrite("{pyname}", &{node.name})')
        #self.out()

    def render_wrapped_field(self, cursor, pyname):
        #pname = self.spell(cursor.semantic_parent)
        pname = self.top_node.name
        name = cursor.spelling
        field_type_name = cu.get_base_type_name(cursor.type)

        wrapper = self.wrapped[field_type_name].wrapper
        extra = ""
        if wrapper == "py::capsule":
            extra = f', "{field_type_name}"'
        result = f"{wrapper}(self.{name}{extra})"
        value = f"const {wrapper}& value"

        self.out('//render_wrapped_field')
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(
            f'[](const {pname}& self)' '{'
            f' return {result};'
            ' },'
            )
            self.out(
            f'[]({pname}& self, {value})' '{'
            f' self.{name} = value;'
            ' }'
            )
        self.out(')')

    #TODO: This is creating memory leaks.  Need wrapper functionality pronto.
    def render_char_ptr_field(self, cursor, pyname):
        #pname = self.spell(cursor.semantic_parent)
        pname = self.top_node.name
        name = cursor.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(
            f'[](const {pname}& self)' '{'
            f' return self.{name};'
            ' },'
            )
            self.out(
            f'[]({pname}& self, const char* source)' '{'
            f' self.{name} = strdup(source);'
            ' }'
            )
        self.out(')')

    def render_fn_ptr_field(self, cursor, pyname):
        #pname = self.spell(cursor.semantic_parent)
        pname = self.top_node.name
        name = cursor.spelling
        typename = cursor.type.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(
            f'[]({pname}& self)' '{'
            f' return self.{name};'
            ' },')
            self.out(
            f'[]({pname}& self, {typename} source)' '{'
            f' self.{name} = source;'
            ' }'
            )
        self.out(')')

    def render_bitfield(self, cursor, pyname):
        #pname = self.spell(cursor.semantic_parent)
        pname = self.top_node.name
        name = cursor.spelling
        typename = cursor.type.spelling
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(
            f'[]({pname}& self)' '{'
            f' return self.{name};'
            ' },')
            self.out(
            f'[]({pname}& self, {typename} source)' '{'
            f' self.{name} = source;'
            ' }'
            )
        self.out(')')

    def is_field_readonly(self, cursor):
        if self.top_node.spec.readonly:
            return True
        if cursor.type.is_const_qualified():
            return True
        if cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        return False
