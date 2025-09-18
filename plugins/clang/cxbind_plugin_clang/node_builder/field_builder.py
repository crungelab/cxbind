from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder
from ..node import FieldNode


class FieldBuilder(NodeBuilder[FieldNode]):
    def create_node(self) -> None:
        self.node = FieldNode(kind='field', name=self.name, cursor=self.cursor)

    def create_pyname(self, name) -> str:
        return self.session.format_field(name)

    def should_cancel(self) -> bool:
        return super().should_cancel() or not self.is_field_mappable(self.cursor)

    def is_field_mappable(self, cursor) -> bool:
        return self.is_cursor_mappable(cursor)
