from loguru import logger
from .node_renderer import NodeRenderer
from .method_renderer import MethodRenderer
from ...node import CtorNode


class CtorRenderer(MethodRenderer):
    def render(self):
        node = self.node
        out = self.out

        if self.node.parent.spec.readonly:
            return

        self.begin_chain()

        arguments = [a for a in node.cursor.get_arguments()]
        if len(arguments):
            arg_types = self.arg_types(arguments)
            if "type-parameter" in arg_types:
                logger.warning(
                    f"Skipping constructor with template parameters: {node.cursor.spelling} in {self.top_node.name} with args {arg_types}"
                )
                return
            out(f".def(py::init<{arg_types}>()")
            self.render_pyargs(arguments, self.node)
            out(")")
        else:
            out(".def(py::init<>())")
