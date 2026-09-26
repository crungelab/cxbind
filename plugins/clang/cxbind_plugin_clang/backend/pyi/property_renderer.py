from ...extra_node import PropertyNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("property")
class PyiPropertyRenderer(PyiNodeRenderer[PropertyNode]):
    def render(self):
        node = self.node
        name = node.first_name
        # getter/setter are C++ expressions, not nodes, so the type is unknown.
        self.context.add_import("typing", "Any")
        self.out("@property")
        self.out(f"def {name}(self) -> Any: ...")
        if not node.readonly:
            self.out(f"@{name}.setter")
            self.out(f"def {name}(self, value: Any) -> None: ...")
