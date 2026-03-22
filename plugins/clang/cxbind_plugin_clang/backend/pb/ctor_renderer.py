from loguru import logger

from ...node import CtorNode

from ..renderer_registry import RendererRegistry

from .method_renderer import MethodRenderer


@RendererRegistry.register("ctor")
class CtorRenderer(MethodRenderer):
    def render(self):
        node = self.node
        out = self.out

        if self.node.parent.spec.readonly:
            return

        self.begin_chain()

        params = node.params
        logger.debug(f"Rendering constructor for {node.name} with params {params}")

        if len(params) > 0:
            arg_types = self.param_types(params)

            out(f".def(py::init<{arg_types}>()")
            self.render_pyargs()
            out(")")
        else:
            out(".def(py::init<>())")
