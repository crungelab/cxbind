from loguru import logger

from .node_builder import NodeBuilder
from ..node import EnumNode


class EnumBuilder(NodeBuilder[EnumNode]):
    def create_node(self):
        self.node = EnumNode(kind='enum', name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.context.format_enum(name)

    def should_cancel(self):
        if self.is_forward_declaration(self.cursor):
            return True
        return super().should_cancel()


    '''
    def build_node(self):
        super().build_node()
        if self.top_node is not None:
            self.top_node.add_child(self.node)
    '''