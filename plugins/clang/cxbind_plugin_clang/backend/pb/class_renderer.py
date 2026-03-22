from . import StructuralRenderer

from ..renderer_registry import RendererRegistry

from ...node import ClassNode


@RendererRegistry.register("class")
class ClassRenderer(StructuralRenderer[ClassNode]):
    pass
