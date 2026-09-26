from typing import TypeVar, Generic

from loguru import logger

from .node_builder import NodeBuilder
from ..node import StructuralNode
from ..pyname_registry import PyBinding, PyKind

T_Node = TypeVar("T_Node", bound=StructuralNode)

class StructuralBuilder(NodeBuilder[T_Node]):
    py_kind = PyKind.TYPE

    def scope_binding(self) -> PyBinding | None:
        # StructuralRenderer declares every class at module scope, nested or not.
        return None

    def register_binding(self) -> None:
        super().register_binding()
        binding = self.node.binding
        # Nested classes are named <Owner><Name>. Store the owner rather than
        # baking in its provisional name; the registry composes the final name.
        if (
            binding is not None
            and not binding.explicit
            and isinstance(self.top_node, StructuralNode)
        ):
            binding.prefix_owner = getattr(self.top_node, "binding", None)

    def should_cancel(self):
        if not self.is_class_bindable(self.cursor):
            return True

        return super().should_cancel()

    def is_class_bindable(self, cursor):
        if not self.is_cursor_visitable(cursor):
            return False
        if not cursor.is_definition():
            return False
        return True
