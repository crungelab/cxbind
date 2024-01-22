from .node_builder import NodeBuilder
from ..node import Method


class MethodBuilder(NodeBuilder[Method]):
    def create_node(self):
        self.node = Method(self.fqname, self.cursor)
