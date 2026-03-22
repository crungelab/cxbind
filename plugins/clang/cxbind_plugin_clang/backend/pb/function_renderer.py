from ...node import FunctionNode

from ..renderer_registry import RendererRegistry

from .functional_renderer import FunctionalRenderer

@RendererRegistry.register("function")
class FunctionRenderer(FunctionalRenderer[FunctionNode]):
    pass