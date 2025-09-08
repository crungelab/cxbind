from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder
from ..node import FieldNode


class FieldBuilder(NodeBuilder[FieldNode]):
    def create_node(self):
        self.node = FieldNode(kind='field', name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.context.format_field(name)

    def should_cancel(self):
        return super().should_cancel() or not self.is_field_mappable(self.cursor)
    
    '''
    def build_node(self):
        super().build_node()
        
        node = self.node
        spec = node.spec
        pyname = spec.pyname or node.pyname
        cursor = self.cursor

        #logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')
        
        self.begin_chain()

        if self.is_field_readonly(cursor):
            self.out(f'.def_readonly("{pyname}", &{node.name})')
        else:
            if self.is_char_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is char*")
                self.visit_char_ptr_field(cursor, pyname)
            elif self.is_function_pointer(cursor):
                #logger.debug(f"{cursor.spelling}: is fn*")
                self.visit_fn_ptr_field(cursor, pyname)
            else:
                self.out(f'.def_readwrite("{pyname}", &{node.name})')
        #self.out()
    '''

    def is_field_mappable(self, cursor):
        return self.is_cursor_mappable(cursor)
