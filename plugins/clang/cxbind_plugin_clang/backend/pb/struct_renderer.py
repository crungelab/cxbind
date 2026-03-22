from . import StructuralRenderer

from ..renderer_registry import RendererRegistry

from ...node import StructNode


@RendererRegistry.register("struct")
class StructRenderer(StructuralRenderer[StructNode]):
    pass
