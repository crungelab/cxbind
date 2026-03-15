from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Generic, Iterable, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import FunctionalSpec, ArgSpec, ArgDirection, ReturnSpec, create_spec
from ..node import Node, FunctionalNode, Argument, ReturnValue, Type
from .node_builder import NodeBuilder

T_Node = TypeVar("T_Node", bound=FunctionalNode)


def _find_matching_angle(s: str, lt: int) -> int:
    depth = 0
    for i in range(lt, len(s)):
        if s[i] == "<":
            depth += 1
        elif s[i] == ">":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_template_args(arg_str: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for i, c in enumerate(arg_str):
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
        elif c == "," and depth == 0:
            args.append(arg_str[start:i].strip())
            start = i + 1
    tail = arg_str[start:].strip()
    if tail:
        args.append(tail)
    return args


def _outer_template_args(spelling: str) -> list[str] | None:
    lt = spelling.find("<")
    if lt == -1:
        return None
    gt = _find_matching_angle(spelling, lt)
    if gt == -1:
        return None
    return _split_template_args(spelling[lt + 1 : gt])


def _replace_outer_template_args(fq: str, resolved_args: list[str]) -> str:
    lt = fq.find("<")
    if lt == -1:
        return fq
    gt = _find_matching_angle(fq, lt)
    if gt == -1:
        return fq

    fq_args = _split_template_args(fq[lt + 1 : gt])
    out_args = fq_args[:]
    for i in range(min(len(out_args), len(resolved_args))):
        out_args[i] = resolved_args[i]

    return f"{fq[:lt]}<{', '.join(out_args)}>{fq[gt + 1:]}"


@dataclass(slots=True)
class ParamInfo:
    name: str
    type: cindex.Type
    cursor: cindex.Cursor | None = None


class FunctionalBuilder(NodeBuilder[T_Node]):
    FUNCTION_CURSOR_KINDS = {
        cindex.CursorKind.FUNCTION_DECL,
        cindex.CursorKind.CXX_METHOD,
        cindex.CursorKind.CONSTRUCTOR,
        cindex.CursorKind.DESTRUCTOR,
        cindex.CursorKind.CONVERSION_FUNCTION,
    }

    TYPEDEF_CURSOR_KINDS = {
        cindex.CursorKind.TYPEDEF_DECL,
        cindex.CursorKind.TYPE_ALIAS_DECL,
    }

    SCALAR_POINTER_OUT_KINDS = {
        cindex.TypeKind.BOOL,
        cindex.TypeKind.CHAR_S,
        cindex.TypeKind.SCHAR,
        cindex.TypeKind.UCHAR,
        cindex.TypeKind.SHORT,
        cindex.TypeKind.USHORT,
        cindex.TypeKind.INT,
        cindex.TypeKind.UINT,
        cindex.TypeKind.LONG,
        cindex.TypeKind.ULONG,
        cindex.TypeKind.LONGLONG,
        cindex.TypeKind.ULONGLONG,
        cindex.TypeKind.FLOAT,
        cindex.TypeKind.DOUBLE,
    }

    def build_node(self):
        super().build_node()
        self.build_args()
        self.build_return_value()

    #
    # -------- normalized signature access --------
    #

    def get_function_type(self) -> cindex.Type | None:
        """
        Return a normalized function type for:
        - function/method declarations
        - typedef/type alias declarations to function types
        - raw FUNCTIONPROTO types
        - pointer-to-function types
        """
        cursor = self.cursor

        # Normal function-like declarations
        if cursor.kind in self.FUNCTION_CURSOR_KINDS:
            t = cursor.type
            if t.kind == cindex.TypeKind.POINTER and t.get_pointee().kind == cindex.TypeKind.FUNCTIONPROTO:
                return t.get_pointee()
            return t

        # Typedef / alias to a function type
        if cursor.kind in self.TYPEDEF_CURSOR_KINDS:
            # Some libclang Python builds expose underlying_typedef_type only on typedefs.
            underlying = getattr(cursor, "underlying_typedef_type", None)
            if underlying is not None:
                func_type = self.unwrap_function_type(underlying)
                if func_type is not None:
                    return func_type

        # Fallback: maybe cursor.type itself is usable
        func_type = self.unwrap_function_type(cursor.type)
        if func_type is not None:
            return func_type

        return None

    def unwrap_function_type(self, t: cindex.Type | None) -> cindex.Type | None:
        if t is None:
            return None

        canon = t.get_canonical()

        if canon.kind == cindex.TypeKind.FUNCTIONPROTO:
            return canon

        if canon.kind == cindex.TypeKind.FUNCTIONNOPROTO:
            return canon

        if canon.kind == cindex.TypeKind.POINTER:
            pointee = canon.get_pointee()
            if pointee.kind in {cindex.TypeKind.FUNCTIONPROTO, cindex.TypeKind.FUNCTIONNOPROTO}:
                return pointee

        return None

    def get_param_infos(self) -> list[ParamInfo]:
        """
        Normalize parameters from either:
        - real parameter cursors on a declaration
        - arg types on a FUNCTIONPROTO
        """
        cursor = self.cursor

        # Best path: real declaration parameters
        if cursor.kind in self.FUNCTION_CURSOR_KINDS:
            infos: list[ParamInfo] = []
            for i, arg_cursor in enumerate(cursor.get_arguments()):
                name = self.make_arg_name(arg_cursor) or f"arg{i}"
                infos.append(ParamInfo(name=name, type=arg_cursor.type, cursor=arg_cursor))
            return infos

        # Typedef / alias / raw function type fallback
        func_type = self.get_function_type()
        if func_type is None:
            return []

        infos = []
        arg_types = self.get_function_arg_types(func_type)
        for i, arg_type in enumerate(arg_types):
            infos.append(ParamInfo(name=f"arg{i}", type=arg_type, cursor=None))
        return infos

    def get_function_arg_types(self, func_type: cindex.Type) -> list[cindex.Type]:
        """
        Extract parameter types from a FUNCTIONPROTO in a way that works across
        libclang Python bindings.
        """
        if func_type.kind not in {cindex.TypeKind.FUNCTIONPROTO, cindex.TypeKind.FUNCTIONNOPROTO}:
            return []

        # Preferred if available in the binding
        argument_types = getattr(func_type, "argument_types", None)
        if callable(argument_types):
            return list(argument_types())

        # Fallback for older bindings
        get_num_arg_types = getattr(func_type, "get_num_arg_types", None)
        get_arg_type = getattr(func_type, "get_arg_type", None)
        if callable(get_num_arg_types) and callable(get_arg_type):
            count = get_num_arg_types()
            return [get_arg_type(i) for i in range(count)]

        return []

    def get_function_result_type(self) -> cindex.Type | None:
        cursor = self.cursor

        if cursor.kind in self.FUNCTION_CURSOR_KINDS:
            return cursor.result_type

        func_type = self.get_function_type()
        if func_type is None:
            return None

        get_result = getattr(func_type, "get_result", None)
        if callable(get_result):
            return get_result()

        # Some bindings may expose spelling but not helper; fall back to cursor.result_type if present
        result_type = getattr(cursor, "result_type", None)
        if result_type is not None:
            return result_type

        return None

    #
    # -------- build args / return --------
    #

    def build_args(self) -> None:
        self.node.args.clear()

        for param in self.get_param_infos():
            spec = self.node.spec.args.get(param.name) if self.node.spec and self.node.spec.args else None

            arg_type = self.build_argument_type(param.type, param.cursor, spec)
            default = self.make_arg_default(param.name, param.cursor, self.node)
            direction = self.make_arg_direction(param.type)

            argument = Argument(
                name=param.name,
                type=arg_type,
                default=default,
                cursor=param.cursor,
                spec=spec,
                direction=direction,
            )
            self.node.args.append(argument)

        logger.debug(f"args: {self.node.args}")

    def build_argument_type(
        self,
        arg_type: cindex.Type,
        arg_cursor: cindex.Cursor | None = None,
        arg_spec: ArgSpec | None = None,
    ) -> Type:
        spelling = self.make_argument_type_spelling(arg_type, arg_cursor)
        base_name = self.get_base_type_name(arg_type)
        logger.debug(f"Argument type spelling: {spelling}, base name: {base_name}")

        base_decl = self.get_base_declaration(arg_type)
        if base_decl is not None:
            base_key = Node.make_key(base_decl)
            logger.debug(f"Base declaration: {base_decl}")
            logger.debug(f"Base kind: {base_decl.kind}")
            logger.debug(f"Base key: {base_key}")
        else:
            base_key = None

        base_spec = self.lookup_spec(base_key)
        logger.debug(f"base_spec: {base_spec}")

        facade = None
        if arg_spec is not None and arg_spec.facade is not None:
            facade = arg_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling,
            base_name=base_name,
            type=arg_type,
            base_spec=base_spec,
            facade=facade,
        )

    def build_return_value(self) -> None:
        logger.debug(f"Building return value for function: {self.name}")

        spec = self.node.returns.spec if self.node.returns is not None else None
        ret_type = self.build_return_type(spec)
        result_type = self.get_function_result_type()

        self.node.returns = ReturnValue(
            type=ret_type,
            cursor=result_type,
            spec=spec,
        )
        logger.debug(f"return value: {self.node.returns}")

    def build_return_type(self, return_spec: ReturnSpec | None = None) -> Type:
        result_type = self.get_function_result_type()
        if result_type is None:
            raise ValueError(f"Cursor {self.cursor.kind} does not expose a function result type")

        spelling = result_type.spelling
        base_name = self.get_base_type_name(result_type)
        logger.debug(f"Return type spelling: {spelling}, base name: {base_name}")

        base_decl = self.get_base_declaration(result_type)
        if base_decl is not None:
            base_key = Node.make_key(base_decl)
            logger.debug(f"Base key: {base_key}")
        else:
            base_key = None

        base_spec = self.lookup_spec(base_key)
        logger.debug(f"base_spec: {base_spec}")

        facade = None
        if return_spec is not None and return_spec.facade is not None:
            facade = return_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling,
            base_name=base_name,
            type=result_type,
            base_spec=base_spec,
            facade=facade,
        )

    #
    # -------- direction / defaults --------
    #

    def make_arg_direction(self, arg_type: cindex.Type) -> ArgDirection:
        arg_type = arg_type.get_canonical()

        if arg_type.kind == cindex.TypeKind.LVALUEREFERENCE:
            pointee = arg_type.get_pointee()
            if not pointee.is_const_qualified():
                return ArgDirection.OUT

        if arg_type.kind == cindex.TypeKind.CONSTANTARRAY:
            return ArgDirection.OUT

        if arg_type.kind == cindex.TypeKind.POINTER:
            ptr = arg_type.get_pointee()
            if not ptr.is_const_qualified() and ptr.kind in self.SCALAR_POINTER_OUT_KINDS:
                return ArgDirection.OUT

        return ArgDirection.IN

    def make_arg_default(
        self,
        arg_name: str,
        argument: cindex.Cursor | None,
        node: FunctionalNode | None = None,
    ) -> str | None:
        # Pure type-based FUNCTIONPROTO parameters do not reliably carry defaults
        if argument is None:
            if node and node.spec.args and arg_name in node.spec.args:
                return node.spec.args[arg_name].default
            return None

        default = self.default_from_tokens(argument.get_tokens())
        logger.debug(f"Initial default value for argument {argument.spelling}: {default}")

        default = self.defaults.get(argument.spelling, default)
        logger.debug(f"Updated default value for argument {argument.spelling}: {default}")

        for child in argument.get_children():
            if child.type.kind == cindex.TypeKind.POINTER:
                default = "nullptr"
            elif (
                child.referenced is not None
                and child.referenced.kind == cindex.CursorKind.ENUM_CONSTANT_DECL
            ):
                ref = child.referenced
                default = f"{ref.type.spelling}::{ref.spelling}"
            elif not default:
                default = self.default_from_tokens(child.get_tokens())

        if node and node.spec.args and argument.spelling in node.spec.args:
            default = node.spec.args[argument.spelling].default
            logger.debug(
                f"Default value for argument {argument.spelling} after processing children: {default}"
            )

        if (
            default is not None
            and isinstance(default, str)
            and default.startswith("{")
            and default.endswith("}")
        ):
            default = f"{self.get_base_type_name(argument.type)}{default}"

        logger.debug(f"Default value for argument {argument.spelling}: {default}")
        return default

    def default_from_tokens(self, tokens) -> str | None:
        parts = "".join(t.spelling for t in tokens).split("=")
        return parts[1] if len(parts) == 2 else None

    #
    # -------- naming / specs / bindability --------
    #

    def create_pyname(self, name: str) -> str:
        return self.format_function(name)

    def should_cancel(self) -> bool:
        return super().should_cancel() or not self.is_function_bindable(self.cursor)

    def find_spec(self) -> FunctionalSpec:
        key = FunctionalNode.make_key(self.cursor, self.is_overloaded(self.cursor))
        spec = self.lookup_spec(key) or create_spec(key)
        return spec

    def process_function_decl(self, decl: cindex.Cursor) -> bool:
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL and self.is_rvalue_ref(param.type):
                logger.debug(f"Found rvalue reference in function {decl.spelling}")
                return False
        return True

    def is_inlined(self, cursor: cindex.Cursor) -> bool:
        return any(tok.spelling == "inline" for tok in cursor.get_tokens())

    def is_function_bindable(self, cursor: cindex.Cursor) -> bool:
        func_type = self.get_function_type()
        if func_type is None:
            return False

        # Declaration-specific checks
        if cursor.kind in self.FUNCTION_CURSOR_KINDS:
            if self.is_inlined(cursor):
                return False
            if not self.is_cursor_bindable(cursor):
                return False
            if cursor.is_deleted_method():
                return False
            if "operator" in cursor.spelling:
                return False
            if cursor.get_num_template_arguments() > 0:
                return False
            if not self.process_function_decl(cursor):
                return False

            for argument in cursor.get_arguments():
                if argument.type.spelling == "va_list":
                    return False

        # Type-based checks
        for arg_type in self.get_function_arg_types(func_type):
            if arg_type.spelling == "va_list":
                return False

        return True

    def is_function_void_return(self, cursor: cindex.Cursor) -> bool:
        result_type = self.get_function_result_type()
        return result_type is not None and result_type.kind == cindex.TypeKind.VOID

    #
    # -------- spelling helpers --------
    #

    def make_argument_type_spelling(
        self,
        arg_type: cindex.Type,
        arg_cursor: cindex.Cursor | None = None,
    ) -> str:
        logger.debug(f"Spelling: {arg_type.spelling}")

        if self.is_function_pointer_type(arg_type):
            logger.debug(f"Function pointer type: {arg_type.spelling}")
            return arg_type.get_canonical().spelling

        canonical = arg_type.get_canonical()
        canonical_spelling = canonical.spelling
        logger.debug(f"Canonical spelling: {canonical_spelling}")

        printing_policy = cindex.PrintingPolicy.create(arg_cursor or self.cursor)
        fq_spelling = arg_type.get_fully_qualified_name(printing_policy)
        logger.debug(f"Fully qualified spelling: {fq_spelling}")

        specialization_node = self.top_node

        def _resolve_templates(spelling: str) -> str:
            if "type-parameter" not in spelling:
                return spelling
            resolved = self.resolve_template_type(
                spelling,
                specialization_node.spec.template_args if specialization_node and specialization_node.spec else {},
            )
            logger.debug(f"Resolved template spelling: {spelling} -> {resolved}")
            return resolved

        def _prefer_fq(canon: str, fq: str) -> str:
            resolved = _resolve_templates(canon)
            if resolved == canon:
                return fq
            resolved_args = _outer_template_args(resolved) or []
            if resolved_args:
                patched = _replace_outer_template_args(fq, resolved_args)
                logger.debug(f"Patched fq spelling: {fq} -> {patched}")
                return patched
            return resolved

        if arg_type.kind == cindex.TypeKind.CONSTANTARRAY:
            logger.debug(f"Constant array type: {arg_type.spelling}")
            element_type = arg_type.get_array_element_type()
            element_canon_spelling = element_type.get_canonical().spelling
            element_fq_spelling = element_type.get_fully_qualified_name(printing_policy)
            element_type_name = self.strip_qualifiers(
                _prefer_fq(element_canon_spelling, element_fq_spelling)
            )
            logger.debug(f"Element type (canon): {element_canon_spelling}")
            logger.debug(f"Element type (fq): {element_fq_spelling}")
            logger.debug(f"Element type (final): {element_type_name}")
            return f"std::array<{element_type_name}, {arg_type.get_array_size()}>&"

        typedef_name = self.typedef_spelling(arg_type)
        if typedef_name is not None:
            return typedef_name

        return _prefer_fq(canonical_spelling, fq_spelling)

    def is_function_pointer_type(self, t: cindex.Type) -> bool:
        canon = t.get_canonical()
        return (
            canon.kind == cindex.TypeKind.POINTER
            and canon.get_pointee().kind in {cindex.TypeKind.FUNCTIONPROTO, cindex.TypeKind.FUNCTIONNOPROTO}
        )

    def resolve_template_type(self, template_param: str, template_mapping) -> str:
        logger.debug(
            f"Resolving template parameter: {template_param} with mapping: {template_mapping}"
        )

        def _to_str(x) -> str:
            for attr in ("spelling", "name"):
                if hasattr(x, attr):
                    return getattr(x, attr)
            return str(x)

        def _lookup(idx: int):
            if isinstance(template_mapping, dict):
                return template_mapping.get(idx, template_mapping.get(str(idx)))
            if 0 <= idx < len(template_mapping):
                return template_mapping[idx]
            return None

        def _repl(m: re.Match) -> str:
            idx = int(m.group(2))
            repl = _lookup(idx)
            return _to_str(repl) if repl is not None else m.group(0)

        return re.sub(r"\btype-parameter-(\d+)-(\d+)\b", _repl, template_param)