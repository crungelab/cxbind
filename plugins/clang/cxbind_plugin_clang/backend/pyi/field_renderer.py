from ...node import FieldNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("field")
class PyiFieldRenderer(PyiNodeRenderer[FieldNode]):
    def render(self):
        self.out(f"{self.node.pyname}: {self.annotation(self.node)}")

    def annotation(self, field: FieldNode) -> str:
        if field.type is not None:
            return self.types.map(field.type)
        return self.types.map_cx(field.cursor.type)
