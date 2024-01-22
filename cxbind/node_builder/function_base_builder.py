from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder, T_Node
from ..node import Function


class FunctionBaseBuilder(NodeBuilder[T_Node]):
    def should_cancel(self):
        return super().should_cancel() or not self.is_function_mappable(self.cursor)

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
                    return False
        return True

    def is_overloaded(self, cursor) -> bool:
        return self.spell(cursor) in self.overloaded

    def is_function_mappable(self, cursor):
        if not self.is_cursor_mappable(cursor):
            return False
        if "operator" in cursor.spelling:
            return False
        if not self.process_function_decl(cursor):
            return False
        for argument in cursor.get_arguments():
            if argument.type.get_canonical().kind == cindex.TypeKind.POINTER:
                ptr = argument.type.get_canonical().get_pointee().kind
                if ptr == cindex.TypeKind.FUNCTIONPROTO:
                    return False
            if argument.type.spelling == "va_list":
                return False
        return True

    def is_function_void_return(self, cursor):
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID

    def should_wrap_function(self, cursor) -> bool:
        if cursor.type.is_function_variadic():
            return True

        result_type = cursor.result_type
        #logger.debug(f"result_type: {result_type.spelling}")
        result_type_name = result_type.spelling.split(" ")[0]
        if result_type_name in self.wrapped:
            return True

        for arg in cursor.get_arguments():
            if arg.type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True
            if self.should_return_argument(arg):
                return True

            #logger.debug(f"wrapped: {arg.spelling}: {self.arg_type(arg)}")
            #logger.debug(self.wrapped)

            type_name = arg.type.spelling.split(" ")[0]
            if type_name in self.wrapped:
                logger.debug(f"Found wrapped {arg.spelling}")
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

    def get_function_result(self, node: Function, cursor) -> str:
        returned = [
            a.spelling for a in cursor.get_arguments() if self.should_return_argument(a)
        ]
        if not self.is_function_void_return(cursor) and not node.omit_ret:
            returned.insert(0, "ret")
        if len(returned) > 1:
            return "std::make_tuple({})".format(", ".join(returned))
        if len(returned) == 1:
            return returned[0]
        return ""

    def get_return_policy(self, cursor) -> str:
        result = cursor.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"

    def write_pyargs(self, arguments, node: Function=None):
        for argument in arguments:
            default = self.default_from_tokens(argument.get_tokens())
            for child in argument.get_children():
                if child.type.kind in [cindex.TypeKind.POINTER]:
                    default = "nullptr"
                elif not len(default):
                    default = self.default_from_tokens(child.get_tokens())
            default = self.defaults.get(argument.spelling, default)
            if node and node.arguments and argument.spelling in node.arguments:
                node_argument = node.arguments[argument.spelling]
                #logger.debug(f"node_argument: {node_argument}")
                #exit()
                #default = node.arguments[argument.spelling].default
                default = str(node_argument['default'])
            # logger.debug(argument.spelling)
            # logger.debug(default)
            if len(default):
                default = " = " + default
            self(f', py::arg("{self.format_field(argument.spelling)}"){default}')

    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""
