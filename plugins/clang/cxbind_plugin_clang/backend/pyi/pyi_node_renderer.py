from typing import Generic, TypeVar

from ...node import Node

from ..renderer import Renderer

T_Node = TypeVar("T_Node", bound=Node)


class PyiNodeRenderer(Renderer, Generic[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__()
        self.node = node

    def render(self):
        # render_node tolerates missing renderers, which is the normal state
        # while stub coverage is being built up.
        for child in self.node.children:
            self.context.render_node(child)
