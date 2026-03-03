from loguru import logger

from .node_builder import NodeBuilder
from ..node import EnumNode


class EnumBuilder(NodeBuilder[EnumNode]):
    def create_node(self):
        self.node = EnumNode(kind='enum', name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.session.format_enum(name)

    def should_cancel(self):
        if self.is_forward_declaration(self.cursor):
            return True
        return super().should_cancel()
