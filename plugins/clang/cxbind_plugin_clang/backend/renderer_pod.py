from ..node import Node
from ..pod import Pod

from .renderer_context import RendererContext


class RendererPod(Pod):
    def __init__(self, node: Node) -> None:
        super().__init__(node)

    @property
    def context(self) -> RendererContext:
        return RendererContext.get_current()
    
    @property
    def out(self) -> RendererContext:
        return self.context.out