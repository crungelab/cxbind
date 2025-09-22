from loguru import logger

from ..node import FunctionTemplateSpecializationNode
from .function_builder import FunctionBuilder


class FunctionTemplateSpecializationBuilder(FunctionBuilder):
    def __init__(self, context, name, cursor=None, spec=None):
        super().__init__(context, name, cursor, spec)

    def create_node(self):
        self.node = FunctionTemplateSpecializationNode(
            kind="function_template_specialization",
            name=self.name,
            pyname=self.create_pyname(self.name),
            cursor=self.cursor,
            spec=self.spec,
        )
