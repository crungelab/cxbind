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

    def finish(self, root: Renderer) -> None:
        # Module-level constants from export_values(), each declared once.
        exports = self.context.pop_exports()
        for name, type_path in exports.items():
            root.out(f"{name}: {type_path}")