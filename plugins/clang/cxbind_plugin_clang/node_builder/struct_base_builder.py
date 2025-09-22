from loguru import logger

from .node_builder import NodeBuilder, T_Node
from ..node import StructBaseNode


class StructBaseBuilder(NodeBuilder[T_Node]):
    def create_pyname(self, name):
        pyname = super().create_pyname(name)
        if isinstance(self.top_node, StructBaseNode):
            return f"{self.top_node.pyname}{pyname}"
        return pyname

    def should_cancel(self):
        if not self.is_class_mappable(self.cursor):
            return True
        """
        # Only map top level classes for now
        if isinstance(self.top_node, StructBaseNode):
            return True
        """

        return super().should_cancel()

    def is_class_mappable(self, cursor):
        if cursor.spelling == "Init":  # TODO: Why?
            return False
        if not self.is_cursor_mappable(cursor):
            return False
        if not cursor.is_definition():
            return False
        return True
