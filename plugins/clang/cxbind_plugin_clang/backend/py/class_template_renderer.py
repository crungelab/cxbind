from loguru import logger

from . import StructBaseRenderer, ClassSpecializationRenderer
from ...node import ClassTemplateNode


class ClassTemplateRenderer(StructBaseRenderer[ClassTemplateNode]):
    def render(self):
        logger.debug(f"ClassTemplateRenderer.render: {self.node}")
        node = self.node
        cursor = node.cursor

        '''
        for specialization in self.node.spec.specializations:
            logger.debug(f"specialization: {specialization}")
            args = ", ".join(specialization.args)
            cname = f"{self.node.name}<{args}>"

            builder = ClassSpecializationRenderer(
                self.context, cname, cursor, specialization
            )
            builder.render()
        '''
        super().render()