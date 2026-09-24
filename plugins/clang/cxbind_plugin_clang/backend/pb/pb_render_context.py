from ...node import Node

from ..render_context import RenderContext
from ..renderer import Renderer


class PbRenderContext(RenderContext):
    def __init__(self) -> None:
        super().__init__()
        # pybind11 `.def(...).def(...)` chaining state; meaningless for other backends.
        self.chaining = False

    def create_renderer(self, node: Node) -> Renderer:
        from .node_renderer_manufacturer import NodeRendererManufacturer

        return NodeRendererManufacturer.create_renderer(node)
