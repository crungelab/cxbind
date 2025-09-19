from loguru import logger

from .function_renderer import FunctionRenderer

class FunctionTemplateSpecializationRenderer(FunctionRenderer):
    def __init__(self, context, node):
        super().__init__(context, node)
