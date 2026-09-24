from loguru import logger

from ...node import ClassTemplateSpecializationNode

from ..renderer_registry import PbRendererRegistry

from .class_renderer import ClassRenderer


@PbRendererRegistry.register("class_template_specialization")
class ClassTemplateSpecializationRenderer(ClassRenderer):
    def __init__(self, node):
        super().__init__(node)
