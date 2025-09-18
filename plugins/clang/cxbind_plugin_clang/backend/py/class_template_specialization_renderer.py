from loguru import logger

from ...node import ClassTemplateSpecializationNode
from .class_renderer import ClassRenderer

class ClassTemplateSpecializationRenderer(ClassRenderer):
    def __init__(self, context, node):
        super().__init__(context, node)
