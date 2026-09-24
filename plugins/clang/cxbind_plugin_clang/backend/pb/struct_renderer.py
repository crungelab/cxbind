from . import StructuralRenderer

from ..renderer_registry import PbRendererRegistry

from ...node import StructNode


@PbRendererRegistry.register("struct")
class StructRenderer(StructuralRenderer[StructNode]):
    pass
