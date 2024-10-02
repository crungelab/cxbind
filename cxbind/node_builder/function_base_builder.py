from clang import cindex
from loguru import logger

from .node_builder import NodeBuilder, T_Node
from ..node import FunctionNode
from .. import cu

class FunctionBaseBuilder(NodeBuilder[T_Node]):
    def should_cancel(self):
        return super().should_cancel() or not self.is_function_mappable(self.cursor)

    def build_node(self):
        super().build_node()

        out = self.out
        node = self.node
        cursor = self.cursor
        arguments = [a for a in cursor.get_arguments()]
        cname = "&" + self.spell(cursor)
        pyname = self.format_field(cursor.spelling)

        if not self.chaining:
            self.begin_chain()
        else:
            out()

        if self.is_overloaded(cursor):
            extra = ""
            if cursor.is_const_method():
                extra = ", py::const_"
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname}{extra})"

        if self.should_wrap_function(cursor):
            out(f'.def("{pyname}", []({self.arg_string(arguments)})')
            with out:
                out("{")
                ret = "" if self.is_function_void_return(cursor) else "auto ret = "

                result = f"{self.spell(cursor)}({self.arg_names(arguments)})"
                result_type: cindex.Cursor = cursor.result_type
                result_type_name = cu.get_base_type_name(result_type)

                if result_type_name in self.wrapped:
                    wrapper = self.wrapped[result_type_name].wrapper
                    extra = ""
                    if wrapper == "py::capsule":
                        extra = f', "{result_type_name}"'
                    result = f"{wrapper}({result}{extra})"

                with out:
                    out(f"{ret}{result};")
                    out(f"return {self.get_function_result(node, cursor)};")
                out("}")
        else:
            out(f'.def("{pyname}", {cname}')
        
        with out:
            self.write_pyargs(arguments, node)
            out(f", {self.get_return_policy(cursor)})")

        #out()

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
                    return False
        return True

    def is_overloaded(self, cursor: cindex.Cursor) -> bool:
        return self.spell(cursor) in self.overloaded

    def is_function_mappable(self, cursor: cindex.Cursor) -> bool:
        if cursor.is_deleted_method():
            return False

        if not self.is_cursor_mappable(cursor):
            return False
        if "operator" in cursor.spelling:
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
        #logger.debug(f"type_name: {result_type_name}")
        if type_name in self.wrapped:
            return True
        return False

    def should_wrap_function(self, cursor) -> bool:
        if cursor.type.is_function_variadic():
            return True

        result_type = cursor.result_type
        #logger.debug(f"result_type: {result_type.spelling}")

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

    def write_pyargs(self, arguments, node: FunctionNode=None):
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
                default = str(node_argument.default)
            # logger.debug(argument.spelling)
            # logger.debug(default)
            if len(default):
                default = " = " + default
            self.out(f', py::arg("{self.format_field(argument.spelling)}"){default}')

    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""
