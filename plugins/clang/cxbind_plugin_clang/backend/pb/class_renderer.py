from . import StructuralRenderer

from ..renderer_registry import PbRendererRegistry

from ...node import ClassNode


@PbRendererRegistry.register("class")
class ClassRenderer(StructuralRenderer[ClassNode]):
    pass
