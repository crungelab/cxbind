from typing import (
    TYPE_CHECKING,
    TypeVar,
    Generic,
    List,
    Dict,
    Tuple,
    Optional,
    Union,
    Any,
    Callable,
    Generator,
)
from contextlib import contextmanager

from loguru import logger

from ...node import Node

from ..renderer import Renderer
from ..render_context import RenderContext

T_Node = TypeVar("T_Node", bound=Node)


class NodeRenderer(Renderer, Generic[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__()
        self.node = node

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.current_session.push_node(node)
        self.out.indent()
        yield node
        self.out.dedent()
        self.current_session.pop_node()

    def render(self):
        for child in self.node.children:
            renderer = self.current_context.create_renderer(child)
            renderer.render()
