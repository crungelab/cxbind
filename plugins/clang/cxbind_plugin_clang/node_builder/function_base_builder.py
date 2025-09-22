from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from .node_builder import NodeBuilder, T_Node
from ..node import FunctionNode
from .. import cu


class FunctionBaseBuilder(NodeBuilder[T_Node]):
    def create_pyname(self, name):
        pyname = self.format_function(name)
        return pyname

    '''
    def create_pyname(self, name):
        pyname = self.format_field(self.cursor.spelling)
        return pyname
    '''

    def should_cancel(self):
        return super().should_cancel() or not self.is_function_mappable(self.cursor)

    def find_spec(self) -> Spec:
        key = None
        if self.is_overloaded(self.cursor):
            key = FunctionNode.make_key(self.cursor, True)
        else:
            key = FunctionNode.make_key(self.cursor)
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

    def is_function_mappable(self, cursor: cindex.Cursor) -> bool:
        if self.is_inlined(cursor):
            return False
        if not self.is_cursor_mappable(cursor):
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

    def should_wrap_function(self, cursor) -> bool:
        if cursor.type.is_function_variadic():
            return True

        result_type = cursor.result_type
        # logger.debug(f"result_type: {result_type.spelling}")

        if self.is_wrapped_type(result_type):
            return True

        for arg in cursor.get_arguments():
            if arg.type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True
            if self.should_return_argument(arg):
                return True
            if self.is_wrapped_type(arg.type):
                return True
        return False

    def should_return_argument(self, argument) -> bool:
        argtype = argument.type.get_canonical()
        if argtype.kind == cindex.TypeKind.LVALUEREFERENCE:
            if not argtype.get_pointee().is_const_qualified():
                return True
        if argtype.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        if argtype.kind == cindex.TypeKind.POINTER:
            ptr = argtype.get_pointee()
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
                return True
        return False

    def get_function_result(self, node: FunctionNode, cursor: cindex.Cursor) -> str:
        returned = [
            a.spelling for a in cursor.get_arguments() if self.should_return_argument(a)
        ]
        if not self.is_function_void_return(cursor) and not node.spec.omit_ret:
            returned.insert(0, "ret")
        if len(returned) > 1:
            return "std::make_tuple({})".format(", ".join(returned))
        if len(returned) == 1:
            return returned[0]
        return ""

    def get_return_policy(self, cursor: cindex.Cursor) -> str:
        result = cursor.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"

    def get_default(self, argument: cindex.Cursor, node: FunctionNode = None):
        default = self.default_from_tokens(argument.get_tokens())
        for child in argument.get_children():
            # logger.debug(f"child: {child.spelling}, {child.kind}, {child.type.spelling}, {child.type.kind}")

            if argument.spelling in self.defaults:
                default = self.defaults.get(argument.spelling, default)
            elif child.type.kind in [cindex.TypeKind.POINTER]:
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
            node_argument = spec.arguments[argument.spelling]
            # logger.debug(f"node_argument: {node_argument}")
            default = str(node_argument.default)

        # Handle complex default values like initializer lists
        if default.startswith("{") and default.endswith("}"):
            # Example: {0, 0} -> SkPoint{0, 0}
            default = f"{cu.get_base_type_name(argument.type)}{default}"

        # logger.debug(argument.spelling)
        # logger.debug(default)
        if len(default):
            default = " = " + default

        return default

    def write_pyargs(self, arguments, node: FunctionNode = None):
        for argument in arguments:
            # logger.debug(f"argument: {argument.spelling}, {argument.kind}, {argument.type.spelling}, {argument.type.kind}")
            default = self.get_default(argument, node)
            self.out(f', py::arg("{self.format_field(argument.spelling)}"){default}')

    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        # logger.debug(f"joined: {joined}")
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""
