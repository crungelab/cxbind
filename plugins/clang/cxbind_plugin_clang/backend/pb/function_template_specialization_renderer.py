from loguru import logger

from ..renderer_registry import RendererRegistry

from .function_renderer import FunctionRenderer


@RendererRegistry.register("function_template_specialization")
class FunctionTemplateSpecializationRenderer(FunctionRenderer):
    def __init__(self, node):
        super().__init__(node)
