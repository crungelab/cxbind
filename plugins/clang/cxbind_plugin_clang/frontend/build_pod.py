from ..node import Node
from ..pod import Pod

from .build_context import BuildContext


class BuildPod(Pod):
    def __init__(self, node: Node) -> None:
        super().__init__(node)

    @property
    def context(self) -> BuildContext:
        return BuildContext.get_current()
    
    @property
    def out(self) -> BuildContext:
        return self.context.out