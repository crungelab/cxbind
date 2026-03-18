from typing import TYPE_CHECKING, TypeVar, Generic
import re

from loguru import logger
from clang import cindex

from cxbind.spec import ParamSpec, ParamDirection

from ...node import Node, Parameter, Type
from ..builder import Builder
from ..functional_build_pod import FunctionalBuildPod, ParamInfo
from .param_builder_helpers import _outer_template_args, _replace_outer_template_args
T_Parameter = TypeVar("T_Parameter", bound=Parameter)


class ParamBuilder(Builder, Generic[T_Parameter]):
    pod: FunctionalBuildPod

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

    def __init__(self, info: ParamInfo):
        super().__init__()
        self.info = info

    def build(self) -> None:
        node = self.pod.node
        self.spec = (
            node.spec.params.get(self.info.name)
            if node.spec and node.spec.params
            else None
        )
        self.facade = self.info.facade
        self.param_type = self.build_param_type(self.info.type, self.info.cursor, self.spec)
        self.default = self.make_param_default(self.info.name, self.info.cursor)
        self.direction = self.make_param_direction(self.info.type)

        self.create_parameter()
        self.build_param()

        logger.debug(f"Adding parameter to node({node.name}): {self.param}")

        node.params.append(self.param)

    def create_parameter(self) -> None:
        self.param = Parameter(
            name=self.info.name,
            type=self.param_type,
            #default=self.default,
            #cursor=self.info.cursor,
            #spec=self.spec,
            #direction=self.direction,
        )

    def build_param(self) -> None:
        self.param.cursor = self.info.cursor
        self.param.default = self.default
        self.param.spec = self.spec
        self.param.facade = self.facade
        self.param.direction = self.direction

    '''
    def build(self) -> None:
        node = self.pod.node
        spec = (
            node.spec.params.get(self.info.name)
            if node.spec and node.spec.params
            else None
        )

        param_type = self.build_param_type(self.info.type, self.info.cursor, spec)
        default = self.make_param_default(self.info.name, self.info.cursor)
        direction = self.make_param_direction(self.info.type)

        parameter = Parameter(
            name=self.info.name,
            type=param_type,
            default=default,
            cursor=self.info.cursor,
            spec=spec,
            direction=direction,
        )
        node.params.append(parameter)
    '''

    def build_param_type(
        self,
        param_type: cindex.Type,
        param_cursor: cindex.Cursor | None = None,
        param_spec: ParamSpec | None = None,
    ) -> Type:
        spelling = self.make_param_type_spelling(param_type, param_cursor)
        base_name = self.get_base_type_name(param_type)
        logger.debug(f"Parameter type spelling: {spelling}, base name: {base_name}")

        base_decl = self.get_base_declaration(param_type)
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
        if param_spec is not None and param_spec.facade is not None:
            facade = param_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling,
            base_name=base_name,
            type=param_type,
            base_spec=base_spec,
            facade=facade,
        )

    def make_param_default(
        self,
        param_name: str,
        param_cursor: cindex.Cursor | None,
    ) -> str | None:
        # Pure type-based FUNCTIONPROTO parameters do not reliably carry defaults
        node = self.pod.node
        if param_cursor is None:
            if node and node.spec.params and param_name in node.spec.params:
                return node.spec.params[param_name].default
            return None

        default = self.default_from_tokens(param_cursor.get_tokens())
        logger.debug(
            f"Initial default value for parameter {param_cursor.spelling}: {default}"
        )

        default = self.defaults.get(param_cursor.spelling, default)
        logger.debug(
            f"Updated default value for parameter {param_cursor.spelling}: {default}"
        )

        for child in param_cursor.get_children():
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

        if node and node.spec.params and param_cursor.spelling in node.spec.params:
            default = node.spec.params[param_cursor.spelling].default
            logger.debug(
                f"Default value for parameter {param_cursor.spelling} after processing children: {default}"
            )

        if (
            default is not None
            and isinstance(default, str)
            and default.startswith("{")
            and default.endswith("}")
        ):
            default = f"{self.get_base_type_name(param_cursor.type)}{default}"

        logger.debug(f"Default value for parameter {param_cursor.spelling}: {default}")
        return default

    def default_from_tokens(self, tokens) -> str | None:
        parts = "".join(t.spelling for t in tokens).split("=")
        return parts[1] if len(parts) == 2 else None

    def make_param_direction(self, param_type: cindex.Type) -> ParamDirection:
        param_type = param_type.get_canonical()

        if param_type.kind == cindex.TypeKind.LVALUEREFERENCE:
            pointee = param_type.get_pointee()
            if not pointee.is_const_qualified():
                return ParamDirection.OUT

        if param_type.kind == cindex.TypeKind.CONSTANTARRAY:
            return ParamDirection.OUT

        if param_type.kind == cindex.TypeKind.POINTER:
            ptr = param_type.get_pointee()
            if (
                not ptr.is_const_qualified()
                and ptr.kind in self.SCALAR_POINTER_OUT_KINDS
            ):
                return ParamDirection.OUT

        return ParamDirection.IN

    def make_param_type_spelling(
        self,
        param_type: cindex.Type,
        param_cursor: cindex.Cursor | None = None,
    ) -> str:
        node = self.pod.node

        logger.debug(f"Spelling: {param_type.spelling}")

        if self.is_function_pointer_type(param_type):
            logger.debug(f"Function pointer type: {param_type.spelling}")
            return param_type.get_canonical().spelling

        canonical = param_type.get_canonical()
        canonical_spelling = canonical.spelling
        logger.debug(f"Canonical spelling: {canonical_spelling}")

        printing_policy = cindex.PrintingPolicy.create(param_cursor or node.cursor)
        fq_spelling = param_type.get_fully_qualified_name(printing_policy)
        logger.debug(f"Fully qualified spelling: {fq_spelling}")

        specialization_node = self.top_node

        def _resolve_templates(spelling: str) -> str:
            if "type-parameter" not in spelling:
                return spelling
            resolved = self.resolve_template_type(
                spelling,
                (
                    specialization_node.spec.template_args
                    if specialization_node and specialization_node.spec
                    else {}
                ),
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

        if param_type.kind == cindex.TypeKind.CONSTANTARRAY:
            logger.debug(f"Constant array type: {param_type.spelling}")
            element_type = param_type.get_array_element_type()
            element_canon_spelling = element_type.get_canonical().spelling
            element_fq_spelling = element_type.get_fully_qualified_name(printing_policy)
            element_type_name = self.strip_qualifiers(
                _prefer_fq(element_canon_spelling, element_fq_spelling)
            )
            logger.debug(f"Element type (canon): {element_canon_spelling}")
            logger.debug(f"Element type (fq): {element_fq_spelling}")
            logger.debug(f"Element type (final): {element_type_name}")
            return f"std::array<{element_type_name}, {param_type.get_array_size()}>&"

        typedef_name = self.typedef_spelling(param_type)
        if typedef_name is not None:
            return typedef_name

        return _prefer_fq(canonical_spelling, fq_spelling)

    def is_function_pointer_type(self, t: cindex.Type) -> bool:
        canon = t.get_canonical()
        return canon.kind == cindex.TypeKind.POINTER and canon.get_pointee().kind in {
            cindex.TypeKind.FUNCTIONPROTO,
            cindex.TypeKind.FUNCTIONNOPROTO,
        }

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
