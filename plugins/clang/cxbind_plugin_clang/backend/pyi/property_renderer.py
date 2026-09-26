from ...extra_node import PropertyNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("property")
class PyiPropertyRenderer(PyiNodeRenderer[PropertyNode]):
    def render(self):
        node = self.node
        name = node.first_name
        annotation = self.types.map(node.getter.returns.type)

        self.out("@property")
        self.out(f"def {name}(self) -> {annotation}: ...")
        if not node.readonly:
            # The value is the setter's last parameter: setX(value) for a
            # method, set(obj*, value) for a free function.
            value = self.types.map(node.setter.params[-1].type)
            self.out(f"@{name}.setter")
            self.out(f"def {name}(self, value: {value}) -> None: ...")
