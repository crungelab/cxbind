from loguru import logger

from ...node import StructuralNode

from .node_renderer import NodeRenderer


class StructuralRenderer[T_Node: StructuralNode](NodeRenderer[T_Node]):
    def render(self):
        node = self.node
        pyname = node.pyname  # resolved via node.binding

        self.end_chain()

        extra = f", {', '.join(node.spec.extends)}" if node.spec.extends else ""

        extra += f",{node.spec.holder}<{node.name}>" if node.spec.holder else ""

        self.out(
            f'py::class_<{node.name}{extra}> _{pyname}(_{self.module_name}, "{pyname}");'
        )
        self.out(f'registry.on(_{self.module_name}, "{pyname}", _{pyname});')

        with self.enter(node):
            # Real members and synthesized extras (inits, __repr__, used
            # functions, properties) are all children, in spec order.
            super().render()

        self.end_chain()
