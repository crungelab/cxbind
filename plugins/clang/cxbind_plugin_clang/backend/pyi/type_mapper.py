"""C++ type -> Python annotation, as pybind11 exposes it."""

from collections import Counter
from typing import Callable

from clang import cindex
from clang.cindex import TypeKind as K

from cxbind.facade import Facade

from ...node import Type
from ...pyname_registry import PyKind, qualified_name
from ...session import Session

AddImport = Callable[..., None]

# pybind11: plain/wide chars are str; signed/unsigned char are int.
CHAR_KINDS = {K.CHAR_S, K.CHAR_U, K.WCHAR, K.CHAR16, K.CHAR32}
INT_KINDS = {
    K.SCHAR, K.UCHAR, K.SHORT, K.USHORT, K.INT, K.UINT,
    K.LONG, K.ULONG, K.LONGLONG, K.ULONGLONG, K.INT128, K.UINT128,
}
FLOAT_KINDS = {K.FLOAT, K.DOUBLE, K.LONGDOUBLE}
INDIRECT_KINDS = {K.POINTER, K.LVALUEREFERENCE, K.RVALUEREFERENCE}
ARRAY_KINDS = {K.CONSTANTARRAY, K.INCOMPLETEARRAY}


def std_name(decl: cindex.Cursor) -> str:
    """Qualified name with inline namespaces (__cxx11, __1) dropped."""
    parts = qualified_name(decl).split("::")
    return "::".join(p for p in parts if not p.startswith("__"))


class TypeMapper:
    def __init__(self, add_import: AddImport) -> None:
        self.add_import = add_import
        # C++ spellings that fell back to Any, for the backend's summary.
        self.unmapped: Counter[str] = Counter()
        self._classes: dict[str, str] | None = None

    # --- bound classes ---------------------------------------------------

    def class_name(self, qualified: str) -> str | None:
        """Python name of a bound C++ type, by qualified C++ name."""
        if self._classes is None:
            self._classes = {}
            for b in Session.get_current().pynames.bindings:
                cursor = getattr(b.node, "cursor", None)
                if b.kind is PyKind.TYPE and cursor is not None:
                    self._classes[qualified_name(cursor)] = b.pyname
        return self._classes.get(qualified)

    # --- entry points ----------------------------------------------------

    def map(self, t: Type) -> str:
        if t.facade is not None:
            return self.map_facade(t.facade, t)
        if t.type is None:
            return self.any(t.spelling)
        return self.map_cx(t.type)

    def map_facade(self, facade: Facade, t: Type) -> str:
        match facade.kind:
            case "vector":
                elem = t.type.get_canonical().get_pointee() if t.type else None
                return f"list[{self.map_cx(elem)}]" if elem else self.any(t.spelling)
            case "buffer":
                self.add_import("collections.abc", "Buffer")
                return "Buffer"
            case "callback":
                self.add_import("collections.abc", "Callable")
                self.add_import("typing", "Any")
                return "Callable[..., Any]"
            case "object":
                self.add_import("typing", "Any")
                return "Any"
            case _:
                return self.any(f"<{facade.kind} facade>")

    def map_cx(self, ct: cindex.Type) -> str:
        c = ct.get_canonical()
        k = c.kind

        if k == K.VOID or k == K.NULLPTR:
            return "None"
        if k == K.BOOL:
            return "bool"
        if k in CHAR_KINDS:
            return "str"
        if k in INT_KINDS:
            return "int"
        if k in FLOAT_KINDS:
            return "float"

        if k in INDIRECT_KINDS:
            pointee = c.get_pointee().get_canonical()
            if k == K.POINTER and pointee.kind in (K.CHAR_S, K.CHAR_U):
                return "str"  # const char* / char*
            if pointee.kind == K.VOID:
                return self.any(c.spelling)
            if pointee.kind == K.FUNCTIONPROTO:
                return self.map_function(pointee)
            return self.map_cx(pointee)

        if k in ARRAY_KINDS:
            elem = c.element_type.get_canonical()
            if elem.kind in (K.CHAR_S, K.CHAR_U):
                return "str"
            return f"list[{self.map_cx(elem)}]"

        if k == K.FUNCTIONPROTO:
            return self.map_function(c)

        if k in (K.RECORD, K.ENUM):
            decl = c.get_declaration()
            bound = self.class_name(qualified_name(decl))
            if bound is not None:
                return bound
            std = self.map_std(c, std_name(decl))
            if std is not None:
                return std

        return self.any(c.spelling)

    # --- helpers ---------------------------------------------------------

    def map_function(self, proto: cindex.Type) -> str:
        self.add_import("collections.abc", "Callable")
        result = self.map_cx(proto.get_result())
        if proto.is_function_variadic():
            return f"Callable[..., {result}]"
        args = ", ".join(self.map_cx(a) for a in proto.argument_types())
        return f"Callable[[{args}], {result}]"

    def map_std(self, c: cindex.Type, name: str) -> str | None:
        def arg(i: int) -> str | None:
            if i >= c.get_num_template_arguments():
                return None
            t = c.get_template_argument_type(i)
            return None if t.kind == K.INVALID else self.map_cx(t)

        def args() -> list[str]:
            out = []
            for i in range(c.get_num_template_arguments()):
                a = arg(i)
                if a is not None:
                    out.append(a)
            return out

        match name:
            case "std::basic_string" | "std::basic_string_view":
                return "str"
            case "std::vector" | "std::array" | "std::list" | "std::deque":
                a = arg(0)
                return f"list[{a}]" if a else None
            case "std::set" | "std::unordered_set":
                a = arg(0)
                return f"set[{a}]" if a else None
            case "std::map" | "std::unordered_map":
                k, v = arg(0), arg(1)
                return f"dict[{k}, {v}]" if k and v else None
            case "std::optional":
                a = arg(0)
                return f"{a} | None" if a else None
            case "std::pair" | "std::tuple":
                return f"tuple[{', '.join(args())}]"
            case "std::variant":
                return " | ".join(args()) or None
            case "std::shared_ptr" | "std::unique_ptr":
                return arg(0)
            case "std::function":
                if c.get_num_template_arguments() > 0:
                    proto = c.get_template_argument_type(0).get_canonical()
                    if proto.kind == K.FUNCTIONPROTO:
                        return self.map_function(proto)
                return None
        return None

    def any(self, spelling: str) -> str:
        self.unmapped[spelling] += 1
        self.add_import("typing", "Any")
        return "Any"
