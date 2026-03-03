from ..node import Node
from ..pod import Pod

from .render_context import RenderContext


class RenderPod(Pod):
    def __init__(self, node: Node) -> None:
        super().__init__(node)

    @property
    def context(self) -> RenderContext:
        return RenderContext.get_current()
    
    @property
    def out(self) -> RenderContext:
        return self.context.out