from ...node import EnumNode

from ..py_enum import PyEnum
from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer
from .type_mapper import py_path

COMPARISONS = ("__lt__", "__gt__", "__le__", "__ge__")
BITWISE = ("__and__", "__rand__", "__or__", "__ror__", "__xor__", "__rxor__")


@PyiRendererRegistry.register("enum")
class PyiEnumRenderer(PyiNodeRenderer[EnumNode]):
    """Stub for py::enum_<T>(scope, name, py::arithmetic()).

    py::enum_ creates a pybind11 class, not an enum.Enum subclass, so the
    stub spells out what pybind11 adds rather than inheriting from enum.
    """

    def render(self):
        node = self.node
        name = node.pyname
        # Full path for self-references: inside a nested class body, a bare
        # name would resolve at module scope, not the enclosing class.
        path = py_path(node.binding) if node.binding is not None else name
        pyenum = PyEnum.from_node(node, self.format_enum_constant)
        # Unscoped enums convert to their underlying type; pybind11 only
        # gives convertible enums the bitwise operators (which return int).
        convertible = not pyenum.scoped

        self.context.add_import("typing", "ClassVar")
        out = self.out

        out(f"class {name}(metaclass=_pybind11_type):")
        with out:
            for constant in pyenum.constants:
                out(f"{constant.name}: ClassVar[{path}]")
            out(f"__members__: ClassVar[dict[str, {path}]]")
            out("def __init__(self, value: int) -> None: ...")
            out("@property")
            out("def name(self) -> str: ...")
            out("@property")
            out("def value(self) -> int: ...")
            out("def __int__(self) -> int: ...")
            out("def __index__(self) -> int: ...")
            for op in COMPARISONS:
                out(f"def {op}(self, other: object) -> bool: ...")
            if convertible:
                for op in BITWISE:
                    out(f"def {op}(self, other: object) -> int: ...")
                out("def __invert__(self) -> int: ...")
        out()

        # Same decision as pb's .export_values(): see PyEnum.exported.
        if pyenum.exported:
            for constant in pyenum.constants:
                self.context.export(constant.name, path)