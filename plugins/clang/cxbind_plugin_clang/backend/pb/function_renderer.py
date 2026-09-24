from ...node import FunctionNode

from ..renderer_registry import PbRendererRegistry

from .functional_renderer import FunctionalRenderer

@PbRendererRegistry.register("function")
class FunctionRenderer(FunctionalRenderer[FunctionNode]):
    pass