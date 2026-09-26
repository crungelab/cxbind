from ...extra_node import ReprNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("repr")
class PyiReprRenderer(PyiNodeRenderer[ReprNode]):
    def render(self):
        self.out("def __repr__(self) -> str: ...")
