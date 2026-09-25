from collections import Counter

from loguru import logger

from ...node import Node

from ..render_context import RenderContext
from ..renderer import Renderer
from ..renderer_registry import PyiRendererRegistry
from .type_mapper import TypeMapper


class PyiRenderContext(RenderContext):
    def __init__(self) -> None:
        super().__init__()
        # (kind, facade) -> count of nodes with no stub renderer yet.
        self.missing: Counter[tuple[str, str | None]] = Counter()
        # (module, name) pairs the rendered stub needs; name None = `import module`.
        self.imports: set[tuple[str, str | None]] = set()
        self.types = TypeMapper(self.add_import)
        # One dict per open scope (module first, then each class being
        # rendered): exported constant name -> its enum's Python path.
        self.export_scopes: list[dict[str, str]] = [{}]

    def add_import(self, module: str, name: str | None = None) -> None:
        self.imports.add((module, name))

    # --- exported enum constants ----------------------------------------

    def export(self, name: str, type_path: str) -> None:
        """Record a constant copied into the current scope by export_values()."""
        scope = self.export_scopes[-1]
        previous = scope.pop(name, None)  # re-insert so order follows last write
        if previous is not None and previous != type_path:
            logger.warning(
                f"exported constant '{name}' from {previous} is overwritten by "
                f"{type_path}; at runtime only the last one survives"
            )
        scope[name] = type_path

    def push_exports(self) -> None:
        self.export_scopes.append({})

    def pop_exports(self) -> dict[str, str]:
        return self.export_scopes.pop()

    # --- renderers -------------------------------------------------------

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