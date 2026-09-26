from ...extra_node import PropertyNode

from ..renderer_registry import PbRendererRegistry
from .node_renderer import NodeRenderer


@PbRendererRegistry.register("property")
class PropertyRenderer(NodeRenderer[PropertyNode]):
    def render(self):
        node = self.node
        name = node.first_name  # the property's Python name
        self.begin_chain()
        if node.readonly:
            self.out(f'.def_property_readonly("{name}", &{node.getter.name})')
        else:
            self.out(f'.def_property("{name}", &{node.getter.name}, &{node.setter.name})')
