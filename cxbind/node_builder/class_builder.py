from . import StructBaseBuilder
from ..node import ClassNode


class ClassBuilder(StructBaseBuilder[ClassNode]):
    def create_node(self):
        self.node = ClassNode(kind='class', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        self.end_chain()

        extra = f",{node.spec.holder}<{node.name}>" if node.spec.holder else ""

        self.out(f'py::class_<{node.name}{extra}> {node.pyname}({self.module}, "{node.pyname}");')
        self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        with self.enter(node):
            self.visit_children(cursor)

            if node.spec.gen_init:
                self.gen_init()
            elif node.spec.gen_kw_init:
                self.gen_kw_init()

        self.end_chain()
