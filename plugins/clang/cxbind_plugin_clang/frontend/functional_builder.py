import re
from typing import Generic, List, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import FunctionalSpec, ArgSpec, ArgDirection, ReturnSpec, create_spec
from ..node import FunctionalNode, Argument, ReturnValue, Type
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
    """Return the outermost template arguments for a spelling like 'Foo<A, B<C>>', or None."""
    lt = spelling.find("<")
    if lt == -1:
        return None
    gt = _find_matching_angle(spelling, lt)
    if gt == -1:
        return None
    return _split_template_args(spelling[lt + 1 : gt])


def _replace_outer_template_args(fq: str, resolved_args: list[str]) -> str:
    """Replace the outermost template args of `fq` with `resolved_args` by position."""
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


class FunctionalBuilder(NodeBuilder[T_Node]):
    def build_node(self):
        super().build_node()
        self.build_args()
        self.build_return_value()

    def build_args(self) -> None:
        #logger.debug(f"Building args for function: {self.name}")
        for arg_cursor in self.cursor.get_arguments():
            arg_name = self.make_arg_name(arg_cursor)
            spec = self.node.spec.args.get(arg_name)
            #logger.debug(f"Node spec: {self.node.spec}")
            #logger.debug(f"Argument {arg_name} spec: {spec}")

            arg_type = self.build_argument_type(arg_cursor, spec)
            default = self.make_arg_default(arg_cursor, self.node)
            direction = self.make_arg_direction(arg_cursor)

            argument = Argument(
                name=arg_name,
                type=arg_type,
                default=default,
                cursor=arg_cursor,
                spec=spec,
                direction=direction,
            )
            self.node.args.append(argument)

        logger.debug(f"args: {self.node.args}")

    def build_argument_type(self, arg_cursor: cindex.Cursor, arg_spec: ArgSpec | None = None) -> Type:
        spelling = self.make_argument_type_spelling(arg_cursor)
        base_name = self.get_base_type_name(arg_cursor.type)
        logger.debug(f"Argument type spelling: {spelling}, base name: {base_name}")
        base_spec = self.lookup_spec(base_name)
        logger.debug(f"type_spec: {base_spec}")

        facade = None
        if arg_spec is not None and arg_spec.facade is not None:
            facade = arg_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling, base_name=base_name, type=arg_cursor.type, base_spec=base_spec, facade=facade
        )

    def build_return_value(self) -> None:
        logger.debug(f"Building return value for function: {self.name}")
        #ret_type = self.cursor.result_type.spelling
        spec = self.node.returns.spec if self.node.returns is not None else None
        ret_type = self.build_return_type(spec)
        self.node.returns = ReturnValue(type=ret_type, cursor=self.cursor.result_type)
        logger.debug(f"return value: {self.node.returns}")

    def build_return_type(self, return_spec: ReturnSpec | None = None) -> Type:
        spelling = self.cursor.result_type.spelling
        base_name = self.get_base_type_name(self.cursor.result_type)
        logger.debug(f"Return type spelling: {spelling}, base name: {base_name}")
        base_spec = self.lookup_spec(base_name)
        logger.debug(f"type_spec: {base_spec}")

        facade = None
        if return_spec is not None and return_spec.facade is not None:
            facade = return_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling, base_name=base_name, type=self.cursor.result_type, base_spec=base_spec, facade=facade
        )

    def make_arg_direction(self, arg_cursor: cindex.Cursor) -> ArgDirection:
        arg_type = arg_cursor.type.get_canonical()
        if arg_type.kind == cindex.TypeKind.LVALUEREFERENCE:
            if not arg_type.get_pointee().is_const_qualified():
                return ArgDirection.OUT
        if arg_type.kind == cindex.TypeKind.CONSTANTARRAY:
            return ArgDirection.OUT
        if arg_type.kind == cindex.TypeKind.POINTER:
            ptr = arg_type.get_pointee()
            kinds = [
                cindex.TypeKind.BOOL,
                cindex.TypeKind.FLOAT,
                cindex.TypeKind.DOUBLE,
                cindex.TypeKind.INT,
                cindex.TypeKind.UINT,
                cindex.TypeKind.USHORT,
                cindex.TypeKind.ULONG,
                cindex.TypeKind.ULONGLONG,
            ]
            if not ptr.is_const_qualified() and ptr.kind in kinds:
                return ArgDirection.OUT
        return ArgDirection.IN

    def make_arg_default(
        self, argument: cindex.Cursor, node: FunctionalNode = None
    ) -> str:
        default = self.default_from_tokens(argument.get_tokens())
        logger.debug(
            f"Initial default value for argument {argument.spelling}: {default}"
        )
        default = self.defaults.get(argument.spelling, default)
        logger.debug(
            f"Updated default value for argument {argument.spelling}: {default}"
        )

        for child in argument.get_children():
            if child.type.kind in [cindex.TypeKind.POINTER]:
                default = "nullptr"
            elif (
                child.referenced is not None
                and child.referenced.kind == cindex.CursorKind.ENUM_CONSTANT_DECL
            ):
                ref = child.referenced
                default = f"{ref.type.spelling}::{ref.spelling}"
            elif not default:
                default = self.default_from_tokens(child.get_tokens())

        if node.spec.args and argument.spelling in node.spec.args:
            default = node.spec.args[argument.spelling].default
            logger.debug(
                f"Default value for argument {argument.spelling} after processing children: {default}"
            )

        # TODO:  Added this for Yoga to initialize default values for aggregate types
        if (
            default is not None
            and type(default) == str
            and default.startswith("{")
            and default.endswith("}")
        ):
            default = f"{self.get_base_type_name(argument.type)}{default}"

        logger.debug(f"Default value for argument {argument.spelling}: {default}")

        return default

    def default_from_tokens(self, tokens) -> str:
        parts = "".join(t.spelling for t in tokens).split("=")
        return parts[1] if len(parts) == 2 else None

    def create_pyname(self, name: str) -> str:
        return self.format_function(name)

    def should_cancel(self) -> bool:
        return super().should_cancel() or not self.is_function_bindable(self.cursor)

    def find_spec(self) -> FunctionalSpec:
        #name = FunctionalNode.spell(self.cursor)
        key = FunctionalNode.make_key(self.cursor, self.is_overloaded(self.cursor))
        spec = self.lookup_spec(key) or create_spec(key)
        #kind = FunctionalNode.make_kind(self.cursor)
        #spec = self.lookup_spec(key) or create_spec(key, kind)
        #spec = self.lookup_spec(name) or create_spec(key, kind)
        #logger.debug(f"FunctionBaseBuilder: find_spec: {spec}")
        return spec

    def process_function_decl(self, decl: cindex.Cursor) -> bool:
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL and self.is_rvalue_ref(
                param.type
            ):
                logger.debug(f"Found rvalue reference in function {decl.spelling}")
                return False
        return True

    def is_inlined(self, cursor: cindex.Cursor) -> bool:
        return any(tok.spelling == "inline" for tok in cursor.get_tokens())

    def is_function_bindable(self, cursor: cindex.Cursor) -> bool:
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
            """
            if self.is_function_pointer(argument):
                return False
            """
            if argument.type.spelling == "va_list":
                return False
        return True

    def is_function_void_return(self, cursor: cindex.Cursor) -> bool:
        return cursor.type.get_result().kind == cindex.TypeKind.VOID

    def make_argument_type_spelling(self, arg_cursor: cindex.Cursor) -> str:
        arg_type = arg_cursor.type
        logger.debug(f"Spelling: {arg_type.spelling}")

        if self.is_function_pointer(arg_cursor):
            logger.debug(f"Function pointer: {arg_cursor.spelling}")
            # return arg_type.get_canonical().get_pointee().spelling
            return arg_type.get_canonical().spelling

        canonical = arg_type.get_canonical()
        canonical_spelling = canonical.spelling
        logger.debug(f"Canonical spelling: {canonical_spelling}")

        printing_policy = cindex.PrintingPolicy.create(arg_cursor)
        fq_spelling = arg_type.get_fully_qualified_name(printing_policy)
        logger.debug(f"Fully qualified spelling: {fq_spelling}")

        specialization_node = self.top_node

        def _resolve_templates(spelling: str) -> str:
            if "type-parameter" not in spelling:
                return spelling
            resolved = self.resolve_template_type(
                spelling, specialization_node.spec.args
            )
            logger.debug(f"Resolved template spelling: {spelling} -> {resolved}")
            return resolved

        def _prefer_fq(canon: str, fq: str) -> str:
            """Use fq spelling, but splice in resolved template args from canonical if needed."""
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
            logger.debug(f"Constant array: {arg_cursor.spelling}")
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

    def resolve_template_type(self, template_param: str, template_mapping) -> str:
        """
        Replace clang-style placeholders like 'type-parameter-0-0' in `template_param`
        using `template_mapping` (a dict or sequence).
        """
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
