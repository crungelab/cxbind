from collections import Counter

from ...node import Node

from ..render_context import RenderContext
from ..renderer import Renderer
from ..renderer_registry import PyiRendererRegistry


class PyiRenderContext(RenderContext):
    def __init__(self) -> None:
        super().__init__()
        # (kind, facade) -> count of nodes with no stub renderer yet.
        self.missing: Counter[tuple[str, str | None]] = Counter()
        # (module, name) pairs the rendered stub needs; name None = `import module`.
        self.imports: set[tuple[str, str | None]] = set()

    def add_import(self, module: str, name: str | None = None) -> None:
        self.imports.add((module, name))

    def create_renderer(self, node: Node) -> Renderer | None:
        facade_kind = node.facade.kind if node.facade else None
        renderer_cls = PyiRendererRegistry.resolve(node.kind, facade_kind)
        if renderer_cls is None:
            self.missing[(node.kind, facade_kind)] += 1
            return None
        return renderer_cls(node)

    def render_node(self, node: Node) -> None:
        # Same as the base, minus the per-node warning; the backend
        # reports one summary instead of thousands of lines.
        renderer = self.create_renderer(node)
        if renderer is not None:
            renderer.render()
