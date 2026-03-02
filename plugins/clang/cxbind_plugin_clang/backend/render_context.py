from typing import TYPE_CHECKING, Type, Optional
import contextlib
from contextvars import ContextVar

from loguru import logger

from cxbind.render_stream import RenderStream

from ..node import Node
from ..worker_context import WorkerContext
from ..session import Session

if TYPE_CHECKING:
    from .renderer import Renderer

current_render_context: ContextVar[Optional["RenderContext"]] = ContextVar("current_render_context", default=None)

class RenderContext(WorkerContext):
    def __init__(self) -> None:
        super().__init__()
        self.out = RenderStream()
        self.chaining = False

    def make_current(self):
        current_render_context.set(self)

    @classmethod
    def get_current(cls) -> Optional["RenderContext"]:
        return current_render_context.get()

    def create_renderer(self, node: Node) -> "Renderer":
        from .pb.node_renderer_table import NODE_RENDERER_TABLE

        cls: Type = NODE_RENDERER_TABLE.get(node.kind, None)
        if cls is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return None
        renderer = cls(node)
        return renderer
