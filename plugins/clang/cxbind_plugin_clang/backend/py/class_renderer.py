from . import StructBaseRenderer
from ...node import ClassNode


class ClassRenderer(StructBaseRenderer[ClassNode]):
    pass

    """
    def render(self):
        node = self.node

        self.end_chain()

        extra = f", {', '.join(node.spec.extends)}" if node.spec.extends else ""

        extra += f",{node.spec.holder}<{node.name}>" if node.spec.holder else ""

        self.out(f'py::class_<{node.name}{extra}> {node.pyname}({self.module}, "{node.pyname}");')
        self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        with self.enter(node):
            super().render()

            if node.spec.gen_init:
                self.gen_init()
            elif node.spec.gen_kw_init:
                self.gen_kw_init()

        self.end_chain()
    """
