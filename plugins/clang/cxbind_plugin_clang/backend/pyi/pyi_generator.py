from ..generator import Generator
from ..renderer import Renderer

from .pyi_node_renderer import PyiNodeRenderer
from .pyi_render_context import PyiRenderContext


class PyiGenerator(Generator):
    context: PyiRenderContext
    indent_body = False

    def __init__(self, source: str, node) -> None:
        super().__init__(PyiRenderContext(), source, node)

    def create_root_renderer(self) -> Renderer:
        return PyiNodeRenderer(self.node)
