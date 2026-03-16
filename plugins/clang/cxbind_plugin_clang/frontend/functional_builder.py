from __future__ import annotations

from typing import TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import (
    Spec,
    FunctionalSpec,
    ReturnSpec,
    create_spec,
)
from ..node import Node, FunctionalNode, Parameter, ReturnValue, Type
from .node_builder import NodeBuilder
from .functional_build_pod import FunctionalBuildPod, ParamInfo
from .param_builder import ParamBuilder

T_Node = TypeVar("T_Node", bound=FunctionalNode)


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

    def __init__(
        self,
        name: str,
        cursor: cindex.Cursor = None,
        spec: Spec = None,
    ) -> None:
        super().__init__(name, cursor, spec)
        self._pod: FunctionalBuildPod | None = None

    @property
    def pod(self) -> FunctionalBuildPod:
        return self._pod

    def build_node(self):
        super().build_node()
        self._pod = FunctionalBuildPod(self.node)
        self.pod.make_current()
        self.build_params()
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
            if (
                t.kind == cindex.TypeKind.POINTER
                and t.get_pointee().kind == cindex.TypeKind.FUNCTIONPROTO
            ):
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
            if pointee.kind in {
                cindex.TypeKind.FUNCTIONPROTO,
                cindex.TypeKind.FUNCTIONNOPROTO,
            }:
                return pointee

        return None

    def get_param_infos(self) -> list[ParamInfo]:
        """
        Normalize parameters from either:
        - real parameter cursors on a declaration
        - param types on a FUNCTIONPROTO
        """
        cursor = self.cursor

        # Best path: real declaration parameters
        if cursor.kind in self.FUNCTION_CURSOR_KINDS:
            infos: list[ParamInfo] = []
            for i, arg_cursor in enumerate(cursor.get_arguments()):
                name = self.make_arg_name(arg_cursor) or f"arg{i}"
                infos.append(
                    ParamInfo(name=name, type=arg_cursor.type, cursor=arg_cursor)
                )
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
        if func_type.kind not in {
            cindex.TypeKind.FUNCTIONPROTO,
            cindex.TypeKind.FUNCTIONNOPROTO,
        }:
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
    # -------- build params / return --------
    #

    def build_params(self) -> None:
        for info in self.get_param_infos():
            builder = ParamBuilder(info)
            builder.build()

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
            raise ValueError(
                f"Cursor {self.cursor.kind} does not expose a function result type"
            )

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
            if param.kind == cindex.CursorKind.PARM_DECL and self.is_rvalue_ref(
                param.type
            ):
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
