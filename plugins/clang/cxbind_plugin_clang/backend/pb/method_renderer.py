from .functional_renderer import FunctionalRenderer

from ..renderer_registry import RendererRegistry

from ...node import MethodNode


@RendererRegistry.register("method")
class MethodRenderer(FunctionalRenderer[MethodNode]):
    pass
