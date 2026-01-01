from typing import List, Optional, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ...node import FunctionNode, Argument
from ... import cu

from .node_renderer import NodeRenderer

T_Node = TypeVar("T_Node", bound=FunctionNode)

class FunctionBaseRenderer(NodeRenderer[T_Node]):
    def render(self):
        out = self.out
        node = self.node
        cursor = node.cursor
        arguments = node.args
        #cname = "&" + node.name
        cname = node.name if node.spec.alias else "&" + node.name
        pyname = node.pyname

        def_call = ""
        if cursor.is_static_method():
            def_call = ".def_static"
        else:
            def_call = ".def"

        self.begin_chain()

        if self.is_overloaded(cursor):
            extra = ""
            if cursor.is_const_method():
                extra = ", py::const_"
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname}{extra})"

        if self.should_wrap_function(cursor):
            is_non_static_method = (
                cursor.kind == cindex.CursorKind.CXX_METHOD
                and not cursor.is_static_method()
            )
            self_arg = f"{self.top_node.name}& self, " if is_non_static_method else ""
            self_call = (
                f"self.{cursor.spelling}"
                if is_non_static_method
                else f"{self.spell(cursor)}"
            )
            out(f'{def_call}("{pyname}", []({self_arg}{self.arg_string(arguments)})')
            with out:
                out("{")
                ret = "" if self.is_function_void_return(cursor) else "auto ret = "
                result = f"{self_call}({self.arg_names(arguments)})"

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
            out(f'{def_call}("{pyname}", {cname}')

        with out:
            self.render_pyargs(arguments)
            out(f", {self.get_return_policy(cursor)})")

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
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

    def arg_types(self, arguments: List[Argument]):
        return ", ".join([a.type for a in arguments])

    def arg_name(self, argument: Argument):
        arg_spelling = argument.name
        if argument.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{arg_spelling}[0]"
        return arg_spelling

    def arg_names(self, arguments: List[Argument]):
        #return ", ".join([a.name for a in arguments])
        return ", ".join([self.arg_name(a) for a in arguments])

    def arg_string(self, arguments: List[Argument]):
        result = []
        for a in arguments:
            arg_type = a.type
            arg_spelling = a.name

            if arg_type.endswith("[]"):
                # Remove the array brackets for the argument type
                arg_type = arg_type[:-2]
                # Add the array brackets to the argument spelling
                arg_spelling = f"{arg_spelling}[]"

            result.append(f"{arg_type} {arg_spelling}")
        return ", ".join(result)

    def render_pyargs(self, arguments: List[Argument]):
        for argument in arguments:
            # logger.debug(f"argument: {argument.spelling}, {argument.kind}, {argument.type.spelling}, {argument.type.kind}")
            default = f" = {argument.default}" if argument.default else ""
            self.out(f', py::arg("{self.format_field(argument.name)}"){default}')

    '''
    def render_pyargs(self, arguments, node: FunctionNode = None):
        for argument in arguments:
            # logger.debug(f"argument: {argument.spelling}, {argument.kind}, {argument.type.spelling}, {argument.type.kind}")
            default = self.get_default(argument, node)
            self.out(f', py::arg("{self.format_field(argument.spelling)}"){default}')
    '''

    '''
    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        # logger.debug(f"joined: {joined}")
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""
    '''