from loguru import logger

from . import StructBaseBuilder, ClassSpecializationBuilder
from ..node import ClassTemplateNode, ClassSpecializationNode


class ClassTemplateBuilder(StructBaseBuilder[ClassTemplateNode]):
    def create_node(self):
        self.node = ClassTemplateNode(
            kind="class_template", name=self.name, cursor=self.cursor
        )
        logger.debug(f"create_node: {self.node}")

    def build_node(self):
        super().build_node()
        logger.debug(f"build_node: {self.node}")
        cursor = self.cursor

        #self.push_node(self.node)
        for specialization in self.node.spec.specializations:
            logger.debug(
                f"specialization: {specialization}"
            )
            args = ", ".join(specialization.args)
            cname = f"{self.node.name}<{args}>"

            # node = ClassNode(kind='class', name=specialization.name, pyname=specialization.name, cursor=self.cursor)
            # node = ClassNode(kind='class', name=cname, pyname=specialization.name, cursor=self.cursor)
            '''
            node = ClassSpecializationNode(
                kind="class_specialization",
                name=cname,
                pyname=specialization.name,
                cursor=self.cursor,
                args=specialization.args,
            )
            '''

            # self.out(f"using {node.name} = {self.node.name}<{args}>;")
            # self.push_node(node)
            #builder = ClassBuilder(self.context, specialization.name, cursor)
            builder = ClassSpecializationBuilder(
                self.context, cname, cursor, specialization
            )
            #self.push_node(builder.node)
            builder.build()
            #self.pop_node()
            # self.pop_node()
        #self.pop_node()
