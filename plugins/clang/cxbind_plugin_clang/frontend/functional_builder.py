import re
from typing import Generic, List, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec
from ..node import FunctionalNode, Argument
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

    def build_args(self) -> None:
        logger.debug(f"Building args for function: {self.name}")
        for a in self.cursor.get_arguments():
            arg_type = self.resolve_argument_type(a)
            arg_spelling = self.arg_spelling(a)

            if arg_type.endswith("[]"):
                arg_type = arg_type[:-2]
                arg_spelling = f"{arg_spelling}[]"

            default = self.get_arg_default(a, self.node)
            spec = self.node.spec.args.get(arg_spelling)
            argument = Argument(
                name=arg_spelling, type=arg_type, default=default, cursor=a, spec=spec
            )
            self.node.args.append(argument)

        logger.debug(f"args: {self.node.args}")

    def get_arg_default(self, argument: cindex.Cursor, node: FunctionalNode = None) -> str:
        default = self.default_from_tokens(argument.get_tokens())
        logger.debug(f"Initial default value for argument {argument.spelling}: {default}")
        default = str(self.defaults.get(argument.spelling, default))
        logger.debug(f"Updated default value for argument {argument.spelling}: {default}")

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
            logger.debug(f"Default value for argument {argument.spelling} after processing children: {default}")

        if default is not None and default.startswith("{") and default.endswith("}"):
            default = f"{self.get_base_type_name(argument.type)}{default}"

        logger.debug(f"Default value for argument {argument.spelling}: {default}")

        return default

    def default_from_tokens(self, tokens) -> str:
        parts = "".join(t.spelling for t in tokens).split("=")
        return parts[1] if len(parts) == 2 else ""

    def create_pyname(self, name: str) -> str:
        return self.format_function(name)

    def should_cancel(self) -> bool:
        return super().should_cancel() or not self.is_function_bindable(self.cursor)

    def find_spec(self) -> Spec:
        key = FunctionalNode.make_key(self.cursor, self.is_overloaded(self.cursor))
        spec = self.lookup_spec(key) or create_spec(key)
        logger.debug(f"FunctionBaseBuilder: find_spec: {spec}")
        return spec

    def process_function_decl(self, decl: cindex.Cursor) -> bool:
        for param in decl.get_children():
            if (
                param.kind == cindex.CursorKind.PARM_DECL
                and self.is_rvalue_ref(param.type)
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

    def is_wrapped_type(self, cursor: cindex.Cursor) -> bool:
        return self.get_base_type_name(cursor) in self.wrapped

    def resolve_argument_type(self, argument: cindex.Cursor) -> str:
        arg_type = argument.type
        logger.debug(f"Spelling: {arg_type.spelling}")

        if self.is_function_pointer(argument):
            logger.debug(f"Function pointer: {argument.spelling}")
            return arg_type.get_canonical().get_pointee().spelling

        canonical = arg_type.get_canonical()
        canonical_spelling = canonical.spelling
        logger.debug(f"Canonical spelling: {canonical_spelling}")

        printing_policy = cindex.PrintingPolicy.create(argument)
        fq_spelling = arg_type.get_fully_qualified_name(printing_policy)
        logger.debug(f"Fully qualified spelling: {fq_spelling}")

        specialization_node = self.top_node

        def _resolve_templates(spelling: str) -> str:
            if "type-parameter" not in spelling:
                return spelling
            resolved = self.resolve_template_type(spelling, specialization_node.spec.args)
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
            logger.debug(f"Constant array: {argument.spelling}")
            element_type = arg_type.get_array_element_type()
            element_canon_spelling = element_type.get_canonical().spelling
            element_fq_spelling = element_type.get_fully_qualified_name(printing_policy)
            element_type_name = _prefer_fq(element_canon_spelling, element_fq_spelling)
            logger.debug(f"Element type (canon): {element_canon_spelling}")
            logger.debug(f"Element type (fq): {element_fq_spelling}")
            logger.debug(f"Element type (final): {element_type_name}")
            return f"std::array<{element_type_name}, {arg_type.get_array_size()}>&"

        type_name = self.get_base_type_name(canonical)
        if type_name in self.wrapped:
            wrapper = self.wrapped[type_name].wrapper
            return f"const {wrapper}&"

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