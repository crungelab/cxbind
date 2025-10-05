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

        arguments = node.args
        logger.debug(f"Rendering constructor for {node.name} with args {arguments}")

        if len(arguments) > 0:
            arg_types = self.arg_types(arguments)

            out(f".def(py::init<{arg_types}>()")
            self.render_pyargs(arguments)
            out(")")
        else:
            out(".def(py::init<>())")
