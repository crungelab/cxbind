from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

from loguru import logger

from cxbind.unit import Unit
from cxbind.code_stream import CodeStream

from ..node import Node
from ..worker_context import WorkerContext

if TYPE_CHECKING:
    from .renderer import Renderer

class RenderContext(WorkerContext):
    def __init__(self, unit: Unit, **kwargs) -> None:
        super().__init__(unit, **kwargs)
        self.out = CodeStream()
        self.chaining = False

    def create_renderer(self, node: Node) -> "Renderer":
        from .py.node_renderer_table import NODE_RENDERER_TABLE

        cls: Type = NODE_RENDERER_TABLE.get(node.kind, None)
        if cls is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return None
        renderer = cls(self, node)
        return renderer
