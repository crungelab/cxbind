from ...node import Node

from ..renderer import Renderer
from ..renderer_registry import RendererRegistry


class NodeRendererManufacturer:
    @staticmethod
    def create_renderer(node: Node) -> Renderer:
        facade_kind = node.facade.kind if node.facade else None

        renderer_cls = RendererRegistry.resolve(node.kind, facade_kind)

        if renderer_cls is None:
            raise ValueError(f"Unsupported node kind={node.kind}, facade={facade_kind}")

        return renderer_cls(node)
