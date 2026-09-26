from ...node import FieldNode

from ..py_field import PyField
from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


# pb dispatches facade fields to their own renderers; the stub must see them too.
@PyiRendererRegistry.register("field")
@PyiRendererRegistry.register("field", "pycapsule")
@PyiRendererRegistry.register("field", "wrapper")
class PyiFieldRenderer(PyiNodeRenderer[FieldNode]):
    def render(self):
        for field in PyField.from_node(self.node, self):
            annotation = self.annotation(field)
            if field.readonly:
                # def_readonly / def_property_readonly: getter only.
                self.out("@property")
                self.out(f"def {field.name}(self) -> {annotation}: ...")
            else:
                self.out(f"{field.name}: {annotation}")

    def annotation(self, field: PyField) -> str:
        node = self.node
        # The node's own Type carries its facade; nested members only have cursors.
        if field.cursor == node.cursor and node.type is not None:
            return self.types.map(node.type)
        return self.types.map_cx(field.cursor.type)