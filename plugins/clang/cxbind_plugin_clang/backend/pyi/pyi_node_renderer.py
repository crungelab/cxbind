from typing import Generic, TypeVar

from ...node import Node

from ..renderer import Renderer
from ..renderer_registry import PyiRendererRegistry

T_Node = TypeVar("T_Node", bound=Node)


class PyiNodeRenderer(Renderer, Generic[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__()
        self.node = node

    @property
    def types(self):
        return self.context.types

    def render(self):
        # render_node tolerates missing renderers, which is the normal state
        # while stub coverage is being built up.
        for child in self.node.children:
            self.context.render_node(child)


# Namespaces don't exist in the Python API: just render their contents.
PyiRendererRegistry.register("namespace")(PyiNodeRenderer)
