from clang import cindex

from ...node import FunctionalNode, Argument

from ..render_pod import RenderPod

from .arg_renderer import ArgRenderer, ARG_RENDERER_TABLE
from .return_renderer import ReturnRenderer

class FunctionalRenderPod(RenderPod):
    node: FunctionalNode
    def __init__(self, node: FunctionalNode):
        super().__init__(node)
        self.return_renderer: ReturnRenderer = None
        self.arg_renderers: list[ArgRenderer] = []
        self.in_arg_renderers: list[ArgRenderer] = []
        self.has_out_args: bool = False
        self.out_args: list[Argument] = []

    def render_input(self):
        for i, arg_renderer in enumerate(self.in_arg_renderers):
            if i > 0:
                self.out << ", "
            arg_renderer.render_input()

    def render_output(self):
        for i, arg_renderer in enumerate(self.arg_renderers):
            if i > 0:
                self.out << ", "
            arg_renderer.render_output()

    def render_out_args(self):
        for i, arg_name in enumerate(self.out_args):
            if i > 0:
                self.out << ", "
            self.out << arg_name

    def is_function_void_return(self):
        cursor = self.node.cursor
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID
