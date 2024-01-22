from .node_builder import NodeBuilder
from ..node import Method


class MethodBuilder(NodeBuilder[Method]):
    def create_node(self):
        self.node = Method(self.fqname, self.cursor)

    def should_cancel(self):
        return super().should_cancel() or not self.is_function_mappable(self.cursor)
