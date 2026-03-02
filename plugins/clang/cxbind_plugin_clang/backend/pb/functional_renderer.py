from typing import List, Optional, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ...node import FunctionalNode, Argument

from .node_renderer import NodeRenderer, RenderContext
from .arg_renderer import ArgRenderer, arg_renderer_table

T_Node = TypeVar("T_Node", bound=FunctionalNode)


class FunctionalRenderer(NodeRenderer[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__(node)
        self.node = node
        self.arg_renderers: List[ArgRenderer] = []
        self.in_arg_renderers: List[ArgRenderer] = []
        self.create_arg_renderers()

    def create_arg_renderers(self):
        for arg in self.node.args:
            facade_kind = arg.spec.facade.kind if arg.spec is not None and arg.spec.facade is not None else None
            renderer_cls = arg_renderer_table.get(facade_kind, ArgRenderer)
            self.arg_renderers.append(renderer_cls(arg))

        excluded_arguments = set()
        for arg_renderer in self.arg_renderers:
            excluded_arguments.update(arg_renderer.excludes())

        self.in_arg_renderers = [arg_renderer for arg_renderer in self.arg_renderers if arg_renderer.arg.name not in excluded_arguments]


    def render(self):
        out = self.out
        node = self.node
        cursor = node.cursor
        arguments = node.args
        # cname = "&" + node.name
        cname = node.name if node.spec.alias else "&" + node.name
        pyname = node.pyname

        def_call = ""
        if cursor.is_static_method():
            def_call = ".def_static"
        else:
            def_call = ".def"

        self.begin_chain()

        if self.is_overloaded(cursor):
            logger.debug(f"Overloaded function rendered: {cursor.spelling}")
            extra = ""
            if cursor.is_const_method():
                extra = ", py::const_"
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname}{extra})"

        if self.should_wrap_function():
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
            out(f'{def_call}("{pyname}", []({self_arg}{self.arg_string()})')
            with out:
                out("{")

                ret = "" if self.is_function_void_return() else "auto ret = "
                result = f"{self_call}({self.arg_names(arguments)})"

                result_type: cindex.Cursor = cursor.result_type
                result_type_name = self.get_base_type_name(result_type)

                if result_type_name in self.wrapped:
                    wrapper = self.wrapped[result_type_name].wrapper
                    extra = ""
                    if wrapper == "py::capsule":
                        extra = f', "{result_type_name}"'
                    result = f"{wrapper}({result}{extra})"

                with out:
                    for arg_renderer in self.arg_renderers:
                        arg_renderer.render()

                    out(f"{ret}{result};")
                    out(f"return {self.get_function_result()};")
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

    def is_function_void_return(self):
        cursor = self.node.cursor
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID

    """
    def is_wrapped_type(self, cursor: cindex.Cursor) -> bool:
        type_name = self.get_base_type_name(cursor)
        # logger.debug(f"type_name: {result_type_name}")
        if type_name in self.wrapped:
            logger.debug(f"Wrapped type: {type_name}")
            return True
        return False
    """
    
    def should_wrap_function(self) -> bool:
        node = self.node
        cursor = node.cursor
        if cursor.type.is_function_variadic():
            return True

        result_type = cursor.result_type
        # logger.debug(f"result_type: {result_type.spelling}")

        if self.is_wrapped_type(result_type):
            return True

        for arg in node.args:
            arg_cursor = arg.cursor
            if arg_cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True
            if self.should_return_argument(arg):
                return True
            if self.is_wrapped_type(arg_cursor.type):
                return True
            if arg.spec is not None and arg.spec.facade is not None:
                return True
        return False

    def should_return_argument(self, argument: Argument) -> bool:
        arg_cursor = argument.cursor
        argtype = arg_cursor.type.get_canonical()
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

    def get_function_result(self) -> str:
        node = self.node
        returned = [a.name for a in node.args if self.should_return_argument(a)]
        if not self.is_function_void_return() and not node.spec.omit_ret:
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
        return ", ".join([arg_renderer.make_pass_string() for arg_renderer in self.arg_renderers])

    def arg_string(self):
        result = []
        for arg_renderer in self.in_arg_renderers:
            result.append(f"{arg_renderer.make_arg_string()}")
        return ", ".join(result)

    def render_pyargs(self, arguments: List[Argument]):
        for arg_renderer in self.in_arg_renderers:
            arg_renderer.make_pyarg_string()
