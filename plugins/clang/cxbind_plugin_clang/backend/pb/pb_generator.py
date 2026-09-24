from ..generator import Generator
from ..renderer import Renderer

from . import NodeRenderer
from .pb_render_context import PbRenderContext


class PbGenerator(Generator):
    def __init__(self, source: str, node) -> None:
        super().__init__(PbRenderContext(), source, node)

    def create_root_renderer(self) -> Renderer:
        # Same as the old Generator(NodeRenderer): the root is a plain NodeRenderer.
        return NodeRenderer(self.node)

    def finish(self, root: Renderer) -> None:
        root.end_chain()
