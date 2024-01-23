from loguru import logger

from .node_builder import NodeBuilder
from ..node import TypedefNode


class TypedefBuilder(NodeBuilder[TypedefNode]):
    def create_node(self):
        self.node = TypedefNode(name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor
        logger.debug(node)
        self.push_node(node)
        self.visit_children(cursor)
        self.pop_node()
