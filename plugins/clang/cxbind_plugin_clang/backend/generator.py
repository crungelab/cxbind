from ..node import RootNode

from .render_context import RenderContext
from .renderer import Renderer


class Generator:
    """Renders one built source through a backend's render context."""

    def __init__(self, context: RenderContext, source: str, node: RootNode) -> None:
        self.context = context
        self.source = source
        self.node = node

    def create_root_renderer(self) -> Renderer:
        raise NotImplementedError(
            f"{type(self).__name__} does not implement create_root_renderer"
        )

    def finish(self, root: Renderer) -> None:
        """Hook run after the root has rendered, inside the output stream."""

    def generate(self) -> str:
        self.context.make_current()
        root = self.create_root_renderer()
        with root.out:
            root.render()
            self.finish(root)
        return root.text
