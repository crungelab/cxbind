from loguru import logger

from . import TemplateBuilder, ClassTemplateSpecializationBuilder
from ..node import ClassTemplateNode


class ClassTemplateBuilder(TemplateBuilder[ClassTemplateNode]):
    def create_node(self):
        self.node = ClassTemplateNode(
            kind="class_template", name=self.name, cursor=self.cursor
        )
        logger.debug(f"create_node: {self.node}")

    def build_node(self):
        super().build_node()
        logger.debug(f"build_node: {self.node}")
        cursor = self.cursor

        for specialization in self.node.spec.specializations:
            logger.debug(f"specialization: {specialization}")
            args = ", ".join(specialization.args)
            cname = f"{self.node.name}<{args}>"

            builder = ClassTemplateSpecializationBuilder(
                self.context, cname, cursor, specialization
            )
            builder.build()

        return True # Don't add this node to parent

    '''
    def build_node(self):
        super().build_node()
        logger.debug(f"build_node: {self.node}")
        cursor = self.cursor

        with self.enter(self.node):
            for specialization in self.node.spec.specializations:
                logger.debug(f"specialization: {specialization}")
                args = ", ".join(specialization.args)
                cname = f"{self.node.name}<{args}>"

                builder = ClassSpecializationBuilder(
                    self.context, cname, cursor, specialization
                )
                builder.build()
    '''