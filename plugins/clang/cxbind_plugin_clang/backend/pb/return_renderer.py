from typing import TYPE_CHECKING, Generic, TypeVar

from loguru import logger
from clang import cindex

from cxbind.facade import (
    Facade,
    PyCapsuleFacade,
    WrapperFacade,
    ObjectFacade,
    VectorFacade,
    BufferFacade,
    CallbackFacade,
)

from loguru import logger
from clang import cindex

from ...node import ReturnValue

from ..renderer import Renderer

if TYPE_CHECKING:
    from .functional_render_pod import FunctionalRenderPod


class ReturnRenderer(Renderer):
    pod: "FunctionalRenderPod"

    def __init__(self, return_value: ReturnValue):
        super().__init__()
        self.return_value = return_value
        self.use_return_temp = False

    def render(self):
        node = self.pod.node
        if (
            self.pod.has_out_args
            and not self.pod.is_function_void_return()
            and not node.spec.omit_ret
        ):
            self.use_return_temp = True
        self.render_prolog()
        self.render_call()
        self.render_epilog()

    def render_prolog(self):
        out = self.out
        node = self.pod.node
        if self.use_return_temp:
            out // "auto _ret = "
        elif self.pod.has_out_args:
            out.write_indent()
        else:
            out // "return "

    def render_call(self):
        self.render_begin_call()
        self.render_end_call()

    def render_begin_call(self):
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

    def render_end_call(self):
        out = self.out
        out << ")"

    def render_epilog(self):
        out = self.out

        out << ";\n"

        if self.pod.has_out_args:
            out // "return std::make_tuple("
            if self.use_return_temp:
                out << "_ret, "
            self.pod.render_out_args()
            out << ");" << out.nl


T_Facade = TypeVar("T_Facade", bound=Facade)


class FacadeReturnRenderer(ReturnRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, return_value: ReturnValue):
        super().__init__(return_value)
        self.facade = return_value.type.facade


class PyCapsuleReturnRenderer(ReturnRenderer):
    def __init__(self, return_value: ReturnValue):
        super().__init__(return_value)
        self.extra: str = ""

    def render_call(self):
        out = self.out
        result_type_name = self.return_value.type.base_name
        self.extra = f'), "{result_type_name}"'
        out << f"py::capsule("
        super().render_call()

    def render_end_call(self):
        out = self.out
        out << f"{self.extra}"

        return super().render_end_call()


class WrapperReturnRenderer(ReturnRenderer):
    def __init__(self, value: ReturnValue):
        super().__init__(value)
        self.extra: str = ""

    def render_call(self):
        out = self.out
        # result_type_name = self.get_base_type_name(self.pod.node.returns.cursor)
        # result_type_name = self.pod.node.returns.type.base_name
        result_type_name = self.return_value.type.base_name
        wrapper = self.wrapped[result_type_name].wrapper
        if wrapper == "pycapsule":
            self.extra = f'), "{result_type_name}"'
        else:
            self.extra = ")"
        out << f"{wrapper}("
        super().render_call()

    def render_end_call(self):
        out = self.out
        out << f"{self.extra}"

        return super().render_end_call()


RETURN_RENDERER_TABLE = {
    "pycapsule": PyCapsuleReturnRenderer,
    "wrapper": WrapperReturnRenderer,
    # "object": ObjectRenderer,
    # "vector": VectorArgRenderer,
    # "callback": CallbackArgRenderer,
    # "buffer": BufferArgRenderer,
}
