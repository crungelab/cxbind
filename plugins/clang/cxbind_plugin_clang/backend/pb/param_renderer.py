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

from ...node import Parameter, Type

from ..render_context import RenderContext
from ..renderer import Renderer


import re


class ParamRenderer(Renderer):
    # Matches the "unnamed function pointer" hole: "(*)", allowing whitespace: "( * )"
    _FN_PTR_HOLE_RE = re.compile(r"\(\s*\*\s*\)")

    def __init__(self, param: Parameter):
        super().__init__()
        self.param = param

    def excludes(self) -> set[str]:
        return set()

    def render_type_and_name(
        self, param_type: Type, param_name: str, private: bool = False
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
        # Example param_type: "bool (*)(int, void *)"
        if self._FN_PTR_HOLE_RE.search(param_type.spelling):
            # Inject name inside the first "(*)"
            injected = self._FN_PTR_HOLE_RE.sub(
                f"(*{param_name})", param_type.spelling, count=1
            )
            out << injected
            return

        # Default case
        out << f"{param_type.spelling} {name_prefix}{param_name}"

    def render_param(self, private: bool = False) -> None:
        out = self.out
        param_type = self.param.type
        param_name = self.param.name

        # Handle C-style "T name[]" where you currently encode "T[]"
        if param_type.spelling.endswith("[]"):
            base_type = param_type.spelling[:-2].rstrip()
            # For arrays, name is part of declarator suffix
            out << f"{base_type} {param_name}[]"
            return

        self.render_type_and_name(param_type, param_name, private=private)

    def render_arg(self, private: bool = False) -> None:
        out = self.out
        prefix = "_" if private else ""

        if self.param.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            out << f"{prefix}&{self.param.name}[0]"
            return

        out << f"{prefix}{self.param.name}"

    def render_pyarg(self):
        param = self.param
        default = f" = {param.default}" if param.default is not None else ""
        self.out(f', py::arg("{self.format_field(param.name)}"){default}')


T_Facade = TypeVar("T_Facade", bound=Facade)


class FacadeParamRenderer(ParamRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, param: Parameter):
        super().__init__(param)
        self.facade = param.type.facade


class PyCapsuleParamRenderer(FacadeParamRenderer[PyCapsuleFacade]):
    def render_param(self, private=False):
        out = self.out
        out << "py::capsule " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        (out << f"static_cast<{self.param.type.spelling}>({param_name}.get_pointer())")


class ObjectParamRenderer(FacadeParamRenderer[ObjectFacade]):
    def render_param(self, private=False):
        out = self.out
        out << "py::object " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        out << f"static_cast<{self.param.type.spelling}>({param_name}.ptr())"


class WrapperParamRenderer(FacadeParamRenderer[WrapperFacade]):
    def render_param(self, private=False):
        out = self.out
        out << f"{self.facade.wrapper} " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        out << f"static_cast<{self.param.type.spelling}>({param_name}.get())"


class VectorParamRenderer(FacadeParamRenderer[VectorFacade]):
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.length_param = self.facade.length_param

    def excludes(self) -> set[str]:
        return {self.length_param}

    def render_param(self, private=False):
        out = self.out
        # out << f"std::vector<{self.param.type.spelling}> " << self.param.name
        out << f"std::vector<{self.param.type.base_name}> " << self.param.name

    def render_arg(self, private=False) -> None:
        super().render_arg(private=True)

    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        value = f"""\
        {param_type.spelling} _{param_name} = ({param_type.spelling}){param_name}.data();
        auto {self.length_param} = {param_name}.size();
        """
        out(value)


class CallbackParamRenderer(FacadeParamRenderer[CallbackFacade]):
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.context_param = self.facade.context_param

        logger.debug(f"CallbackParamRenderer: {self.param}")
        for child in self.param.cursor.get_children():
            logger.debug(f"CallbackParamRenderer child kind: {child.kind}")
            child_type = child.type
            logger.debug(f"CallbackParamRenderer child type: {child_type.spelling}")
            logger.debug(f"CallbackParamRenderer child type kind: {child_type.kind}")
            child_decl = child_type.get_declaration()
            logger.debug(f"CallbackParamRenderer child declaration: {child_decl.kind}")
            for parm_cursor in child_decl.get_children():
                logger.debug(f"CallbackParamRenderer child parameter: {parm_cursor.spelling} type: {parm_cursor.type.spelling}")

    def excludes(self) -> set[str]:
        return {self.context_param}

    def render_param(self, private=False):
        out = self.out
        out << f"py::function " << self.param.name

    def render_arg(self, private=False) -> None:
        super().render_arg(private=True)

    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        value = f"""\
        cxbind::thunk_state _{self.context_param}({param_name});
        auto {self.context_param} = &_{self.context_param};
        auto _{param_name} = +[](int value, void* ctx) -> bool {{
            auto& ts = *static_cast<cxbind::thunk_state*>(ctx);
            // ... use ts, acquire GIL, call Python, etc ...
            py::gil_scoped_acquire gil;
            py::object result = ts.cb(value);
            return result.cast<bool>();
        }};
        """
        out(value)


class BufferParamRenderer(FacadeParamRenderer[BufferFacade]):
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.length_param = self.facade.length_param

    def make_facade_type(self):
        if self.param.optional or self.param.default is not None:
            return f"std::optional<py::buffer>"
        else:
            return "py::buffer"

    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        info_name = f"{self.param.name.camelCase()}Info"

        size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"

        logger.debug(
            f"BufferArgWrapper: {self.param.name} type: {self.param.type.spelling.get()} size_expr: {size_expr}"
        )

        if self.param.optional or self.param.default is not None:
            value = f"""\
            py::buffer_info {info_name} = {param_name}.has_value() ? {param_name}.value().request() : py::buffer_info();
            {param_type} {self.param.annotation} _{param_name} = ({param_type} {self.param.annotation}){info_name}.ptr;
            auto {self.length_param.name.camelCase()} = {size_expr};
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {param_name}.request();
            {param_type} {self.param.annotation} _{param_name} = ({param_type} {self.param.annotation}){info_name}.ptr;
            auto {self.length_param.name.camelCase()} = {size_expr};
            """

        out(value)


PARAM_RENDERER_TABLE = {
    "pycapsule": PyCapsuleParamRenderer,
    "wrapper": WrapperParamRenderer,
    "object": ObjectParamRenderer,
    "vector": VectorParamRenderer,
    "callback": CallbackParamRenderer,
    "buffer": BufferParamRenderer,
}
