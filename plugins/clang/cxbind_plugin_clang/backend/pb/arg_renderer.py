from typing import Generic, TypeVar

from loguru import logger
from clang import cindex

from cxbind.facade import (
    ArgFacade,
    WrapperArgFacade,
    ObjectArgFacade,
    VectorArgFacade,
    BufferArgFacade,
    CallbackArgFacade,
)

from ...node import Argument

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

    def make_arg_type_string(self) -> str:
        # Whatever your generator currently stores (string spelling).
        # Ex: "int", "const char *", "bool (*)(int, void *)", "Foo[]"
        return self.arg.type
    
    def render_type_and_name(self, arg_type: str, arg_name: str, private: bool = False, first: bool = False) -> str:
        out = self.out
        """
        Render a single C/C++ parameter declarator.

        - Normal:    "int x"
        - Array:     "float x[]"
        - Fn ptr:    "bool (*cb)(int, void *)"   (injects name into "(*)")
        """
        prefix = ", " if not first else ""
        name_prefix = "_" if private else ""

        # Function pointer case: type contains "(*)"
        # Example arg_type: "bool (*)(int, void *)"
        if self._FN_PTR_HOLE_RE.search(arg_type):
            # Inject name inside the first "(*)"
            injected = self._FN_PTR_HOLE_RE.sub(f"(*{arg_name})", arg_type, count=1)
            out << injected

        # Default case
        out << f"{prefix}{arg_type} {name_prefix}{arg_name}"

    def render_input(self, first: bool = False, private: bool = False) -> None:
        """
        if self.arg.is_out:
            return
        """
        out = self.out
        prefix = ", " if not first else ""
        arg_type = self.make_arg_type_string()
        arg_name = self.arg.name

        # Handle C-style "T name[]" where you currently encode "T[]"
        if arg_type.endswith("[]"):
            base_type = arg_type[:-2].rstrip()
            # For arrays, name is part of declarator suffix
            out << f"{prefix}{base_type} {arg_name}[]"
            return

        if self.is_wrapped_type(self.arg.cursor.type):
            base_type = self.get_base_type_name(self.arg.cursor.type)
            wrapped_spec = self.wrapped.get(base_type)
            logger.debug(f"Wrapped spec for type {self.arg.type}: {wrapped_spec}")
            if wrapped_spec and wrapped_spec.wrapper:
                out << f"{prefix}const {wrapped_spec.wrapper}& {arg_name}"
                """
                if len(self.pod.in_arg_renderers) > 1 and first:
                    out << ", "
                """
                return

        #out  << self.render_type_and_name(arg_type, arg_name, private=private) << suffix

        self.render_type_and_name(arg_type, arg_name, private=private, first=first)

    def render_output(self, first: bool = False, private: bool = False) -> None:
        out = self.out
        prefix = ", " if not first else ""
        prefix += "_" if private else ""

        if self.arg.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            out << f"{prefix}&{self.arg.name}[0]"
            return

        if self.is_wrapped_type(self.arg.cursor.type):
            result_type_name = self.get_base_type_name(self.arg.cursor.type)
            wrapper = self.wrapped[result_type_name].wrapper
            extractor = "get_pointer" if wrapper == "py::capsule" else "get"
            #out << f"{prefix}{self.arg.name}.get()"
            out << f"{prefix}{self.arg.name}.{extractor}()"
            return
        
        out << f"{prefix}{self.arg.name}"

    def render_pyarg(self):
        argument = self.arg
        default = f" = {argument.default}" if argument.default is not None else ""
        self.out(f', py::arg("{self.format_field(argument.name)}"){default}')


T_Facade = TypeVar("T_Facade", bound=ArgFacade)


class ArgFacadeRenderer(ArgRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.facade = arg.spec.facade

class WrapperArgRenderer(ArgFacadeRenderer[WrapperArgFacade]):
    def make_arg_type_string(self):
        return f"py::object"

    def render_output(self):
        return f"static_cast<{self.arg.type}>({super().render_output()}.ptr())"


class ObjectArgRenderer(ArgFacadeRenderer[ObjectArgFacade]):
    def make_arg_type_string(self):
        return f"py::object"

    def render_output(self):
        return f"static_cast<{self.arg.type}>({super().render_output()}.ptr())"


class VectorArgRenderer(ArgFacadeRenderer[VectorArgFacade]):
    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.length_arg = self.facade.length_arg

    def excludes(self) -> set[str]:
        return {self.length_arg}

    def make_arg_type_string(self):
        base_type = self.get_base_type_name(self.arg.cursor.type)
        return f"std::vector<{base_type}>"

    def render_input(self, first: bool = False) -> None:
        super().render_input(first, private=False)

    def render_output(self, first: bool = False) -> None:
        super().render_output(first, private=True)

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        value = f"""\
        {arg_type} _{arg_name} = ({arg_type}){arg_name}.data();
        auto {self.length_arg} = {arg_name}.size();
        """
        out(value)


class CallbackArgRenderer(ArgFacadeRenderer[CallbackArgFacade]):
    def __init__(self, arg: Argument):
        super().__init__(arg)
        self.context_arg = self.facade.context_arg

    """
    def excludes(self) -> set[str]:
        return {self.context_arg}
    """

    def make_arg_type_string(self):
        return f"py::function"

    def render_output(self, first: bool = False) -> None:
        super().render_output(first, private=True)

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        value = f"""\
        auto _{arg_name} = +[](int, void* ctx) -> bool {{
            auto* st = static_cast<OverlapThunkState*>(ctx);
            // ... use st, acquire GIL, call Python, etc ...
            return true;
        }};
        """
        out(value)


class BufferArgRenderer(ArgFacadeRenderer[BufferArgFacade]):
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
            f"BufferArgWrapper: {self.arg.name} type: {self.arg.type.name.get()} size_expr: {size_expr}"
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


arg_renderer_table = {
    "wrapper": WrapperArgRenderer,
    "object": ObjectArgRenderer,
    "vector": VectorArgRenderer,
    "callback": CallbackArgRenderer,
    "buffer": BufferArgRenderer,
}
