from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

from loguru import logger

from cxbind.emission import Emission

from ..node import Node
from ..worker_context import WorkerContext
from ..session import Session

if TYPE_CHECKING:
    from .renderer import Renderer

class RenderContext(WorkerContext):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.out = Emission()
        self.chaining = False

    def create_renderer(self, node: Node) -> "Renderer":
        from .py.node_renderer_table import NODE_RENDERER_TABLE

        cls: Type = NODE_RENDERER_TABLE.get(node.kind, None)
        if cls is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return None
        renderer = cls(self, node)
        return renderer
