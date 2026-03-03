from typing import List, Optional, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ...node import FunctionalNode, Argument

from .node_renderer import NodeRenderer, RenderContext
from .arg_renderer import ArgRenderer, arg_renderer_table
from .return_renderer import ReturnRenderer
from .functional_render_pod import FunctionalRenderPod

T_Node = TypeVar("T_Node", bound=FunctionalNode)


class FunctionalRenderer(NodeRenderer[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__(node)
        self.node = node
        self.my_pod = FunctionalRenderPod(node)
        self.my_pod.return_renderer = ReturnRenderer(node.returns)
        self.create_arg_renderers()

    def create_arg_renderers(self):
        for arg in self.node.args:
            facade_kind = (
                arg.spec.facade.kind
                if arg.spec is not None and arg.spec.facade is not None
                else None
            )
            renderer_cls = arg_renderer_table.get(facade_kind, ArgRenderer)
            self.my_pod.arg_renderers.append(renderer_cls(arg))

        excluded_arguments = set()
        for arg_renderer in self.my_pod.arg_renderers:
            excluded_arguments.update(arg_renderer.excludes())

        self.my_pod.in_arg_renderers = [
            arg_renderer
            for arg_renderer in self.my_pod.arg_renderers
            if arg_renderer.arg.name not in excluded_arguments
        ]

    def render(self):
        self.my_pod.make_current()

        out = self.out
        node = self.node
        cursor = node.cursor
        arguments = node.args
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
            # out(f'{def_call}("{pyname}", []({self_arg}{self.arg_string()})')
            out // f'{def_call}("{pyname}", []({self_arg}'
            self.my_pod.render_input()
            out << ")" << out.nl

            with out:
                out("{")

                ret = "" if self.my_pod.is_function_void_return() else "auto ret = "

                """
                self.context.push_stream("output")
                self.render_output()
                text = self.context.pop_stream().text
                result = f"{self_call}({text})"
                """

                # result = f"{self_call}({self.render_output()})"

                result_type: cindex.Cursor = cursor.result_type
                result_type_name = self.get_base_type_name(result_type)

                """
                if result_type_name in self.wrapped:
                    wrapper = self.wrapped[result_type_name].wrapper
                    extra = ""
                    if wrapper == "py::capsule":
                        extra = f', "{result_type_name}"'
                    result = f"{wrapper}({result}{extra})"
                """
                with out:
                    for arg_renderer in self.my_pod.arg_renderers:
                        arg_renderer.render()

                    #out(f"{ret}{result};")
                    #out // f"{ret}{self_call}("
                    out // f"return {self_call}("
                    self.my_pod.render_output()
                    out << ");\n"
                    # out(f"return {self.make_function_result()};")
                    # self.render_return(ret)
                out("}")
        else:
            out(f'{def_call}("{pyname}", {cname}')

        with out:
            self.render_pyargs()
            out(f", {self.get_return_policy(cursor)})")

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
                    return False
        return True

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
            if arg.is_out:
                logger.debug(
                    f"Found out parameter in function {node.cursor.spelling}, argument {arg.name}"
                )
                return True
            if self.is_wrapped_type(arg_cursor.type):
                return True
            if arg.spec is not None and arg.spec.facade is not None:
                return True
        return False

    """
    def render_return(self, has_ret:bool = False) -> None:
        ret = "ret" if has_ret else ""
        out = self.out
        node = self.node
        out_args = [arg.name for arg in node.args]
        has_out_args = any(arg.is_out for arg in node.args)
        #logger.debug(f"Function {node.cursor.spelling} will return: {out_args}")
        if not self.is_function_void_return() and not node.spec.omit_ret:
            # out_args.insert(0, "ret")
            # out << "ret, "
            out // f"return {ret};" << out.nl

        elif has_out_args:
            # return "std::make_tuple({})".format(", ".join(out_args))
            out // "return std::make_tuple("
            self.render_output()
            out << ");" << out.nl
        elif len(out_args) == 1:
            return out_args[0]
    """

    """
    def make_function_result(self) -> str:
        node = self.node
        out_args = [arg.name for arg in node.args]
        has_out_args = any(arg.is_out for arg in node.args)
        logger.debug(f"Function {node.cursor.spelling} will return: {out_args}")
        if not self.is_function_void_return() and not node.spec.omit_ret:
            out_args.insert(0, "ret")
        if has_out_args:
            return "std::make_tuple({})".format(", ".join(out_args))
        if len(out_args) == 1:
            return out_args[0]
        return ""
    """

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

    def render_pyargs(self):
        for arg_renderer in self.my_pod.in_arg_renderers:
            arg_renderer.render_pyarg()
