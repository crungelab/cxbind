from .node_renderer import NodeRenderer

from ..renderer_registry import RendererRegistry

from ...node import NamespaceNode


@RendererRegistry.register("namespace")
class NamespaceRenderer(NodeRenderer[NamespaceNode]):
    pass
