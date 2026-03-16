from clang import cindex

from ...node import FunctionalNode, Parameter

from ..render_pod import RenderPod

from .param_renderer import ParamRenderer, PARAM_RENDERER_TABLE
from .return_renderer import ReturnRenderer

class FunctionalRenderPod(RenderPod):
    node: FunctionalNode
    def __init__(self, node: FunctionalNode):
        super().__init__(node)
        self.return_renderer: ReturnRenderer = None
        self.arg_renderers: list[ParamRenderer] = []
        self.param_renderers: list[ParamRenderer] = []
        self.has_out_params: bool = False
        self.out_params: list[Parameter] = []

    def render_params(self):
        for i, param_renderer in enumerate(self.param_renderers):
            if i > 0:
                self.out << ", "
            param_renderer.render_param()

    def render_args(self):
        for i, arg_renderer in enumerate(self.arg_renderers):
            if i > 0:
                self.out << ", "
            arg_renderer.render_arg()

    def render_out_args(self):
        for i, arg_name in enumerate(self.out_params):
            if i > 0:
                self.out << ", "
            self.out << arg_name

    def is_function_void_return(self):
        cursor = self.node.cursor
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID
