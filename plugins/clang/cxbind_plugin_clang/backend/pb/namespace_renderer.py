from .node_renderer import NodeRenderer

from ..renderer_registry import PbRendererRegistry

from ...node import NamespaceNode


@PbRendererRegistry.register("namespace")
class NamespaceRenderer(NodeRenderer[NamespaceNode]):
    pass
