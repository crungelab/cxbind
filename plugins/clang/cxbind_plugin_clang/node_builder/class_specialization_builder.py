from loguru import logger

from ..node import ClassSpecializationNode
from .class_builder import ClassBuilder

class ClassSpecializationBuilder(ClassBuilder):
    def __init__(self, context, name, cursor = None, spec = None):
        super().__init__(context, name, cursor)
        self.spec = spec

    def find_spec(self):
        return self.spec
    
    def create_node(self):
        self.node = ClassSpecializationNode(
            kind="class_specialization",
            name=self.name,
            pyname=self.create_pyname(self.name),
            cursor=self.cursor,
            spec=self.spec,
        )

