from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder
from ..node import Field


class FieldBuilder(NodeBuilder[Field]):
    def create_node(self):
        self.node = Field(self.fqname, self.cursor)

    def create_pyname(self, name):
        return self.context.format_field(name)

    def should_cancel(self):
        return super().should_cancel() or not self.is_field_mappable(self.cursor)
    
    def build_node(self):
        super().build_node()
        
        node = self.node
        cursor = self.cursor

        #logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')
        
        if self.is_field_readonly(cursor):
            self(f'{self.scope}.def_readonly("{node.pyname}", &{node.fqname});')
        else:
            if self.is_char_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is char*")
                self.visit_char_ptr_field(cursor, node.pyname)
            elif self.is_fn_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is fn*")
                self.visit_fn_ptr_field(cursor, node.pyname)
            else:
                self(f'{self.scope}.def_readwrite("{node.pyname}", &{node.fqname});')

    #TODO: This is creating memory leaks.  Need wrapper functionality pronto.
    def visit_char_ptr_field(self, cursor, pyname):
        pname = self.spell(cursor.semantic_parent)
        name = cursor.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[](const {pname}& self)' '{'
            f' return self.{name};'
            ' },'
            )
            self(
            f'[]({pname}& self, std::string source)' '{'
            ' char* c = (char *)malloc(source.size() + 1);'
            ' strcpy(c, source.c_str());'
            f' self.{name} = c;'
            ' }'
            )
        self(');')

    def visit_fn_ptr_field(self, cursor, pyname):
        pname = self.spell(cursor.semantic_parent)
        name = cursor.spelling
        typename = cursor.type.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[]({pname}& self)' '{'
            f' return self.{name};'
            ' },')
            self(
            f'[]({pname}& self, {typename} source)' '{'
            f' self.{name} = source;'
            ' }'
            )
        self(');')

    def is_field_mappable(self, cursor):
        return self.is_cursor_mappable(cursor)

    def is_field_readonly(self, cursor):
        if self.top_node.readonly:
            return True
        if cursor.type.is_const_qualified():
            return True
        if cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        return False
