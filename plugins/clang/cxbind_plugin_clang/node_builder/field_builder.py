from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder
from ..node import FieldNode


class FieldBuilder(NodeBuilder[FieldNode]):
    def create_node(self):
        self.node = FieldNode(kind='field', name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.session.format_field(name)

    def should_cancel(self):
        return super().should_cancel() or not self.is_field_mappable(self.cursor)

    def is_field_mappable(self, cursor):
        return self.is_cursor_mappable(cursor)
