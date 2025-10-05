import re

from typing import Generic, List, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ..node import FunctionBaseNode, Argument
from .. import cu

from .node_builder import NodeBuilder

T_Node = TypeVar("T_Node", bound=FunctionBaseNode)


class FunctionBaseBuilder(NodeBuilder[T_Node]):
    def build_node(self):
        super().build_node()
        self.build_args()

    def build_args(self) -> None:
        logger.debug(f"Building args for function: {self.name}")
        for a in self.cursor.get_arguments():
            arg_type = self.resolve_argument_type(a)
            arg_spelling = self.arg_spelling(a)

            if arg_type.endswith("[]"):
                # Remove the array brackets for the argument type
                arg_type = arg_type[:-2]
                # Add the array brackets to the argument spelling
                arg_spelling = f"{arg_spelling}[]"

            # self.node.args.append(f"{arg_type} {arg_spelling}")
            default = self.get_arg_default(a, self.node)
            argument = Argument(
                type=arg_type, name=arg_spelling, default=default, cursor=a
            )
            self.node.args.append(argument)

        logger.debug(f"args: {self.node.args}")

    def get_arg_default(self, argument: cindex.Cursor, node: FunctionBaseNode = None):
        # logger.debug(f"Getting default for argument: {argument.spelling}")
        default = self.default_from_tokens(argument.get_tokens())
        # default = self.defaults.get(argument.spelling, default)
        default = str(self.defaults.get(argument.spelling, default))
        for child in argument.get_children():
            # logger.debug(f"child: {child.spelling}, {child.kind}, {child.type.spelling}, {child.type.kind}")

            if child.type.kind in [cindex.TypeKind.POINTER]:
                default = "nullptr"
            elif (
                child.referenced is not None
                and child.referenced.kind == cindex.CursorKind.ENUM_CONSTANT_DECL
            ):
                referenced = child.referenced
                # logger.debug(f"referenced: {referenced.spelling}, {referenced.kind}, {referenced.type.spelling}, {referenced.type.kind}")
                default = f"{referenced.type.spelling}::{referenced.spelling}"
            elif not len(default):
                default = self.default_from_tokens(child.get_tokens())

        spec = node.spec
        if spec.arguments and argument.spelling in spec.arguments:
            spec_argument = spec.arguments[argument.spelling]
            # logger.debug(f"node_argument: {node_argument}")
            default = str(spec_argument.default)

        # Handle complex default values like initializer lists
        if default.startswith("{") and default.endswith("}"):
            # Example: {0, 0} -> SkPoint{0, 0}
            default = f"{cu.get_base_type_name(argument.type)}{default}"

        # logger.debug(f"Default for {argument.spelling}: {default}")
        # logger.debug(f"defaults: {self.defaults}")

        return default

    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        # logger.debug(f"joined: {joined}")
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""

    def create_pyname(self, name):
        pyname = self.format_function(name)
        return pyname

    def should_cancel(self):
        return super().should_cancel() or not self.is_function_bindable(self.cursor)

    def find_spec(self) -> Spec:
        key = None
        if self.is_overloaded(self.cursor):
            key = FunctionBaseNode.make_key(self.cursor, True)
        else:
            key = FunctionBaseNode.make_key(self.cursor)
        spec = self.lookup_spec(key)
        if spec is None:
            spec = create_spec(key)

        logger.debug(f"FunctionBaseBuilder: find_spec: {spec}")
        return spec

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
                    return False
        return True

    def is_inlined(self, cursor: cindex.Cursor) -> bool:
        tokens = list(cursor.get_tokens())
        if any(tok.spelling == "inline" for tok in tokens):
            # logger.debug(f"{cursor.spelling} is explicitly inline")
            return True
        return False

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
            if self.is_function_pointer(argument):
                return False
            if argument.type.spelling == "va_list":
                return False
        return True

    def is_function_void_return(self, cursor: cindex.Cursor):
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID

    def is_wrapped_type(self, cursor: cindex.Cursor) -> bool:
        type_name = cu.get_base_type_name(cursor)
        # logger.debug(f"type_name: {result_type_name}")
        if type_name in self.wrapped:
            return True
        return False

    def resolve_argument_type(self, argument: cindex.Cursor):
        arg_kind = argument.kind
        # logger.debug(f"arg_kind: {arg_kind}")
        arg_type = argument.type
        # logger.debug(arg_type.spelling)
        arg_type_kind = arg_type.kind
        # logger.debug(arg_type_kind)
        if self.is_function_pointer(argument):
            logger.debug(f"Function pointer: {argument.spelling}")
            return argument.type.get_canonical().get_pointee().spelling

        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            logger.debug(f"Constant array: {argument.spelling}")
            element_type = argument.type.get_array_element_type()
            element_type_name = cu.get_base_type_name(
                argument.type.get_array_element_type()
            )
            logger.debug(f"Element type: {element_type.spelling}")
            logger.debug(f"Element type kind: {element_type.kind}")
            if element_type.kind == cindex.TypeKind.UNEXPOSED:
                resolved_type = element_type.get_canonical()
                specialization_node = self.top_node
                resolved_type_name = self.resolve_template_type(
                    resolved_type.spelling, specialization_node.spec.args
                )
                logger.debug(f"Resolved type: {resolved_type_name}")
                element_type_name = resolved_type_name

            return f"std::array<{element_type_name}, {argument.type.get_array_size()}>&"

        # Handle template parameters (placeholders)
        if arg_type_kind == cindex.TypeKind.UNEXPOSED:
            specialization_node = self.top_node
            logger.debug(f"specialization_node: {specialization_node}")
            logger.debug(f"specialization_node.spec: {specialization_node.spec}")
            # Attempt to get the canonical type spelling for the template argument
            resolved_type = argument.type.get_canonical()
            resolved_type_name = self.resolve_template_type(
                resolved_type.spelling, specialization_node.spec.args
            )
            logger.debug(f"Resolved template parameter: {resolved_type}")
            logger.debug(f"Resolved template parameter: {resolved_type_name}")
            return resolved_type_name

        type_name = cu.get_base_type_name(argument.type)
        # logger.debug(f"arg_type: {type_name}")

        if "type-parameter" in type_name:
            logger.debug(f"arg_type: {type_name}")
            specialization_node = self.top_node
            logger.debug(f"specialization_node: {specialization_node}")
            logger.debug(f"specialization_node.spec: {specialization_node.spec}")
            # Attempt to get the canonical type spelling for the template argument
            resolved_type = argument.type.get_canonical()
            resolved_type_name = self.resolve_template_type(
                resolved_type.spelling, specialization_node.spec.args
            )
            logger.debug(f"Resolved template parameter: {resolved_type}")
            logger.debug(f"Resolved template parameter: {resolved_type_name}")
            return resolved_type_name

        if type_name in self.wrapped:
            wrapper = self.wrapped[type_name].wrapper
            return f"const {wrapper}&"

        return argument.type.get_canonical().spelling

    def resolve_template_type(self, template_param: str, template_mapping):
        """
        Replace clang-style placeholders like 'type-parameter-0-0' in `template_param`
        using `template_mapping`.

        - If `template_mapping` is a list/tuple, the replacement uses the second index
        in the placeholder (the position), e.g. 'type-parameter-0-0' -> mapping[0].
        - If it's a dict, it tries keys `idx` (int) or `str(idx)`.
        - Works when the placeholder is embedded in larger strings.
        """
        logger.debug(
            f"Resolving template parameter: {template_param} with mapping: {template_mapping}"
        )

        def _to_str(x):
            # Gracefully stringify mapped objects (e.g., clang types with .spelling/.name)
            for attr in ("spelling", "name"):
                if hasattr(x, attr):
                    return getattr(x, attr)
            return str(x)

        def _lookup(idx: int):
            if isinstance(template_mapping, dict):
                return template_mapping.get(idx, template_mapping.get(str(idx)))
            # assume sequence
            if 0 <= idx < len(template_mapping):
                return template_mapping[idx]
            return None

        # Replace all occurrences of type-parameter-<depth>-<index>
        pattern = re.compile(r"\btype-parameter-(\d+)-(\d+)\b")

        def _repl(m: re.Match):
            # depth = int(m.group(1))  # currently unused; depth==0 in most common cases
            idx = int(m.group(2))
            repl = _lookup(idx)
            return _to_str(repl) if repl is not None else m.group(0)

        return pattern.sub(_repl, template_param)
