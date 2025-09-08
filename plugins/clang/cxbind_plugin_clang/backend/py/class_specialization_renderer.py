from loguru import logger

from ...node import ClassSpecializationNode
from .class_renderer import ClassRenderer

class ClassSpecializationRenderer(ClassRenderer):
    def __init__(self, context, node):
        super().__init__(context, node)
