from loguru import logger

from ..node import ClassTemplateSpecializationNode
from .class_builder import ClassBuilder


class ClassTemplateSpecializationBuilder(ClassBuilder):
    def __init__(self, name, cursor=None, spec=None):
        super().__init__(name, cursor, spec)

    def create_node(self):
        self.node = ClassTemplateSpecializationNode(
            kind="class_template_specialization",
            name=self.name,
            pyname=self.create_pyname(self.name),
            cursor=self.cursor,
            spec=self.spec,
        )
