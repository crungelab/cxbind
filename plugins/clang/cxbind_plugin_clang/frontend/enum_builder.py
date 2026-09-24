from loguru import logger

from .node_builder import NodeBuilder
from ..node import EnumNode
from ..pyname_registry import PyKind


class EnumBuilder(NodeBuilder[EnumNode]):
    py_kind = PyKind.TYPE

    def create_node(self):
        self.node = EnumNode(kind='enum', name=self.name, cursor=self.cursor)

    def should_cancel(self):
        if self.is_forward_declaration(self.cursor):
            return True
        return super().should_cancel()
