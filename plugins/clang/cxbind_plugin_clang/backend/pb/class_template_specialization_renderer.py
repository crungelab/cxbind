from loguru import logger

from ...node import ClassTemplateSpecializationNode

from ..renderer_registry import RendererRegistry

from .class_renderer import ClassRenderer


@RendererRegistry.register("class_template_specialization")
class ClassTemplateSpecializationRenderer(ClassRenderer):
    def __init__(self, node):
        super().__init__(node)
