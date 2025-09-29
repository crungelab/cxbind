from loguru import logger

from ..node import FunctionTemplateNode
from . import FunctionTemplateSpecializationBuilder
from . import TemplateBuilder

class FunctionTemplateBuilder(TemplateBuilder[FunctionTemplateNode]):
    def create_node(self):
        self.node = FunctionTemplateNode(
            kind="function_template", name=self.name, cursor=self.cursor
        )
        #logger.debug(f"create_node: {self.node}")

    def build_node(self):
        super().build_node()
        #logger.debug(f"build_node: {self.node}")
        cursor = self.cursor

        for specialization in self.node.spec.specializations:
            #logger.debug(f"specialization: {specialization}")
            args = ", ".join(specialization.args)
            cname = f"{self.node.name}<{args}>"

            builder = FunctionTemplateSpecializationBuilder(
                self.context, cname, cursor, specialization
            )
            builder.build()

        return True # Don't add this node to parent
