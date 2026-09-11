from loguru import logger

from .node_builder import NodeBuilder
from ..node import NamespaceNode


class NamespaceBuilder[T_Node: NamespaceNode](NodeBuilder[T_Node]):
    def create_node(self):
        self.node = NamespaceNode(kind="namespace", name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()
        logger.debug(f"Building namespace node: {self.name}, node: {self.node}")
        node = self.node
        cursor = self.cursor

        with self.enter(node):
            self.visit_children(cursor)
