from loguru import logger

from .node_builder import NodeBuilder
from ..node import Field


class FieldBuilder(NodeBuilder[Field]):
    def create_node(self):
        self.node = Field(self.fqname, self.cursor)

    def create_pyname(self, name):
        return self.context.format_field(name)

    def build_node(self):
        super().build_node()
        
        node = self.node
        cursor = self.cursor

        logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')
        
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
