from typing import TYPE_CHECKING

from loguru import logger
from clang import cindex

from ...node import ReturnValue

from ..renderer import Renderer

if TYPE_CHECKING:
    from .functional_render_pod import FunctionalRenderPod


class ReturnRenderer(Renderer):
    pod: "FunctionalRenderPod"

    def __init__(self, value: ReturnValue):
        super().__init__()
        self.value = value

    def render(self):
        #out = self.out
        self.render_prolog()
        self.render_call()
        self.render_epilog()
        #out << ");\n"

    def render_prolog(self):
        out = self.out
        node = self.pod.node
        if self.pod.has_out_args:
            out.write_indent()
        else:
            out // f"return "

    def render_call(self):
        out = self.out
        node = self.pod.node
        cursor = node.cursor

        is_non_static_method = (
            cursor.kind == cindex.CursorKind.CXX_METHOD
            and not cursor.is_static_method()
        )

        self_call = (
            f"self.{cursor.spelling}"
            if is_non_static_method
            else f"{self.spell(cursor)}"
        )

        out << f"{self_call}("
        self.pod.render_output()

    def render_epilog(self):
        out = self.out
        node = self.pod.node

        #self.pod.render_output()
        out << ");\n"

        if self.pod.has_out_args:
            # return "std::make_tuple({})".format(", ".join(out_args))
            out // "return std::make_tuple("
            self.pod.render_out_args()
            out << ");" << out.nl

    """
    def render_epilog(self):
        out = self.out
        #self.pod.render_output()
        out << ");\n"
    """

class WrapperReturnRenderer(ReturnRenderer):
    def __init__(self, value: ReturnValue):
        super().__init__(value)

    def render_call(self):
        out = self.out
        #base_type = self.get_base_type(self.pod.node.returns.cursor)
        #logger.debug(f"Base type: {base_type}, spelling: {base_type.spelling}")
        #result_type_name = base_type.spelling
        result_type_name = self.get_base_type_name(self.pod.node.returns.cursor)
        wrapper = self.wrapped[result_type_name].wrapper
        extra = ""
        if wrapper == "py::capsule":
            extra = f', "{result_type_name}"'
        logger.debug(f"Wrapper: {wrapper}, extra: {extra}")
        #result = f"{wrapper}({result}{extra})"
        out << f"{wrapper}("
        super().render_call()
        #out << f"{extra})"
        out << f")"
        """
        if len(self.pod.arg_renderers) > 0:
            out << ", "
        """
