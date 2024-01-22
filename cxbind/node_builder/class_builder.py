from . import StructBaseBuilder
from ..node import Class


class ClassBuilder(StructBaseBuilder[Class]):
    def create_node(self):
        self.node = Class(self.fqname, self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        self(f"PYCLASS_BEGIN({self.module}, {node.fqname}, {node.pyname})")
        with self.enter(node):
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        self(f"PYCLASS_END({self.module}, {node.fqname}, {node.pyname})\n")
