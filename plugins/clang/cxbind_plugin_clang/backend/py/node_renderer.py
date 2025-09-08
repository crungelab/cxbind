from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ...node import Node

from ..renderer import Renderer
from ..render_context import RenderContext

T_Node = TypeVar("T_Node", bound=Node)


class NodeRenderer(Renderer, Generic[T_Node]):
    def __init__(
        self,
        context: RenderContext,
        node: T_Node
    ) -> None:
        super().__init__(context)
        self.node = node

    def create_pyname(self, name) -> str:
        return self.format_type(name)

    def find_spec(self) -> Spec:
        key = Node.make_key(self.node.cursor)
        spec = self.lookup_spec(key)
        return spec
