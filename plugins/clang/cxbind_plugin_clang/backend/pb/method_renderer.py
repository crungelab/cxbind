from .functional_renderer import FunctionalRenderer

from ..renderer_registry import PbRendererRegistry

from ...node import MethodNode


@PbRendererRegistry.register("method")
class MethodRenderer(FunctionalRenderer[MethodNode]):
    pass
