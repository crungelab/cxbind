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
            template_args = specialization.template_args
            logger.debug(f"specialization: {specialization}")
            args = ", ".join(template_args)
            cname = f"{self.node.name}<{args}>"

            builder = ClassTemplateSpecializationBuilder(
                cname, args, cursor, specialization
            )
            with self.context.override_template_args(template_args):
                builder.build()

        return True # Don't add this node to parent

    def register_node(self):
        pass # Don't register this node, only its specializations