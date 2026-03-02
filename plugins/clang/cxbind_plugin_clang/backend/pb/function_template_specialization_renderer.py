from loguru import logger

from .function_renderer import FunctionRenderer

class FunctionTemplateSpecializationRenderer(FunctionRenderer):
    def __init__(self, node):
        super().__init__(node)
