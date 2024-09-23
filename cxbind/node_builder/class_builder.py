from . import StructBaseBuilder
from ..node import ClassNode


class ClassBuilder(StructBaseBuilder[ClassNode]):
    def create_node(self):
        self.node = ClassNode(kind='class', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        extra = f",{node.holder}<{node.name}>" if node.holder else ""

        #self.out(f"PYCLASS_BEGIN({self.module}, {node.name}, {node.pyname} {extra})")
        self.out(f"PYCLASS({self.module}, {node.name}, {node.pyname} {extra})")
        with self.enter(node):
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        #self.out(f"PYCLASS_END({self.module}, {node.name}, {node.pyname})")
        self.out(";")
