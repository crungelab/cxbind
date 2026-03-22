from typing import Generic, TypeVar

from loguru import logger
from clang import cindex

from cxbind.facade import Facade

from ....node import Parameter, Type

from ...render_context import RenderContext
from ...renderer import Renderer


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
