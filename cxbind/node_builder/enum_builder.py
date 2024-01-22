from .node_builder import NodeBuilder
from ..node import Enum


class EnumBuilder(NodeBuilder[Enum]):
    def create_node(self):
        self.node = Enum(self.fqname, self.cursor)
    def create_pyname(self, name):
        return self.context.format_enum(name)
