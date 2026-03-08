from typing import Generic, TypeVar

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

from ...node import Argument, Type

from ..render_context import RenderContext
from ..renderer import Renderer


import re


class ArgRenderer(Renderer):
    # Matches the "unnamed function pointer" hole: "(*)", allowing whitespace: "( * )"
    _FN_PTR_HOLE_RE = re.compile(r"\(\s*\*\s*\)")

    def __init__(self, arg: Argument):
        super().__init__()
        self.arg = arg

    def excludes(self) -> set[str]:
        return set()

    def render_type_and_name(
        self, arg_type: Type, arg_name: str, private: bool = False
    ) -> str:
        out = self.out
        """
        Render a single C/C++ parameter declarator.

        - Normal:    "int x"
        - Array:     "float x[]"
        - Fn ptr:    "bool (*cb)(int, void *)"   (injects name into "(*)")
        """
        name_prefix = "_" if private else ""

        # Function pointer case: type contains "(*)"
        # Example arg_type: "bool (*)(int, void *)"
        if self._FN_PTR_HOLE_RE.search(arg_type.spelling):
            # Inject name inside the first "(*)"
            injected = self._FN_PTR_HOLE_RE.sub(
                f"(*{arg_name})", arg_type.spelling, count=1
            )
            out << injected
            return

        # Default case
        out << f"{arg_type.spelling} {name_prefix}{arg_name}"

    def render_input(self, private: bool = False) -> None:
        out = self.out
        arg_type = self.arg.type
        arg_name = self.arg.name

        # Handle C-style "T name[]" where you currently encode "T[]"
        if arg_type.spelling.endswith("[]"):
            base_type = arg_type.spelling[:-2].rstrip()
            # For arrays, name is part of declarator suffix
            out << f"{base_type} {arg_name}[]"
            return

        self.render_type_and_name(arg_type, arg_name, private=private)

    def render_output(self, private: bool = False) -> None:
        out = self.out
        prefix = "_" if private else ""

        if self.arg.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            out << f"{prefix}&{self.arg.name}[0]"
            return

        out << f"{prefix}{self.arg.name}"

    def render_pyarg(self):
        argument = self.arg
        default = f" = {argument.default}" if argument.default is not None else ""
        self.out(f', py::arg("{self.format_field(argument.name)}"){default}')


T_Facade = TypeVar("T_Facade", bound=Facade)


class FacadeArgRenderer(ArgRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.facade = arg.type.facade


class PyCapsuleArgRenderer(FacadeArgRenderer[PyCapsuleFacade]):
    def render_input(self, private=False):
        out = self.out
        out << "py::capsule " << self.arg.name

    def render_output(self):
        out = self.out
        arg_name = self.arg.name
        (out << f"static_cast<{self.arg.type.spelling}>({arg_name}.get_pointer())")


class ObjectArgRenderer(FacadeArgRenderer[ObjectFacade]):
    def render_input(self, private=False):
        out = self.out
        out << "py::object " << self.arg.name

    def render_output(self):
        out = self.out
        arg_name = self.arg.name
        out << f"static_cast<{self.arg.type.spelling}>({arg_name}.ptr())"


class WrapperArgRenderer(FacadeArgRenderer[WrapperFacade]):
    def render_input(self, private=False):
        out = self.out
        out << f"{self.facade.wrapper} " << self.arg.name

    def render_output(self):
        out = self.out
        arg_name = self.arg.name
        out << f"static_cast<{self.arg.type.spelling}>({arg_name}.get())"


class VectorArgRenderer(FacadeArgRenderer[VectorFacade]):
    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.length_arg = self.facade.length_arg

    def excludes(self) -> set[str]:
        return {self.length_arg}

    def render_input(self, private=False):
        out = self.out
        # out << f"std::vector<{self.arg.type.spelling}> " << self.arg.name
        out << f"std::vector<{self.arg.type.base_name}> " << self.arg.name

    def render_output(self, private=False) -> None:
        super().render_output(private=True)

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        value = f"""\
        {arg_type.spelling} _{arg_name} = ({arg_type.spelling}){arg_name}.data();
        auto {self.length_arg} = {arg_name}.size();
        """
        out(value)


class CallbackArgRenderer(FacadeArgRenderer[CallbackFacade]):
    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.context_arg = self.facade.context_arg

    def excludes(self) -> set[str]:
        return {self.context_arg}

    def render_input(self, private=False):
        out = self.out
        out << f"py::function " << self.arg.name

    def render_output(self, private=False) -> None:
        super().render_output(private=True)

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        value = f"""\
        cxbind::thunk_state _{self.context_arg}({arg_name});
        auto {self.context_arg} = &_{self.context_arg};
        auto _{arg_name} = +[](int value, void* ctx) -> bool {{
            auto& ts = *static_cast<cxbind::thunk_state*>(ctx);
            // ... use ts, acquire GIL, call Python, etc ...
            py::gil_scoped_acquire gil;
            py::object result = ts.cb(value);
            return result.cast<bool>();
        }};
        """
        out(value)


class BufferArgRenderer(FacadeArgRenderer[BufferFacade]):
    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.length_arg = self.facade.length_arg

    def make_facade_type(self):
        if self.arg.optional or self.arg.default is not None:
            return f"std::optional<py::buffer>"
        else:
            return "py::buffer"

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        info_name = f"{self.arg.name.camelCase()}Info"

        size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"

        logger.debug(
            f"BufferArgWrapper: {self.arg.name} type: {self.arg.type.spelling.get()} size_expr: {size_expr}"
        )

        if self.arg.optional or self.arg.default is not None:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.has_value() ? {arg_name}.value().request() : py::buffer_info();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_arg.name.camelCase()} = {size_expr};
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.request();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_arg.name.camelCase()} = {size_expr};
            """

        out(value)


ARG_RENDERER_TABLE = {
    "pycapsule": PyCapsuleArgRenderer,
    "wrapper": WrapperArgRenderer,
    "object": ObjectArgRenderer,
    "vector": VectorArgRenderer,
    "callback": CallbackArgRenderer,
    "buffer": BufferArgRenderer,
}
