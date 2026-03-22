from typing import (
    TypeVar,
    Generic,
    Any,
    Generator,
)
from contextlib import contextmanager

from loguru import logger

from ...node import Node

from ..renderer import Renderer

T_Node = TypeVar("T_Node", bound=Node)


class NodeRenderer(Renderer, Generic[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__()
        self.node = node

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.session.push_node(node)
        self.out.indent()
        yield node
        self.out.dedent()
        self.session.pop_node()

    def render(self):
        for child in self.node.children:
            renderer = self.context.create_renderer(child)
            renderer.render()
