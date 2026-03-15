from typing import List, Optional, TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec
from cxbind.facade import Facade

from ...node import FunctionalNode, Argument

from .node_renderer import NodeRenderer, RenderContext
from .arg_renderer import ArgRenderer, ARG_RENDERER_TABLE
from .return_renderer import ReturnRenderer, RETURN_RENDERER_TABLE
from .functional_render_pod import FunctionalRenderPod

T_Node = TypeVar("T_Node", bound=FunctionalNode)


class FunctionalRenderer(NodeRenderer[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__(node)
        self.node = node
        self.my_pod = FunctionalRenderPod(node)
        self.create_arg_renderers()
        self.create_return_renderer()

    def create_arg_renderers(self):
        node = self.node
        logger.debug(f"Creating argument renderers for node: {node.name}")

        for arg in node.args:
            facade_kind = arg.type.facade.kind if arg.type.facade is not None else None
            renderer_cls = ARG_RENDERER_TABLE.get(facade_kind, ArgRenderer)
            logger.debug(f"Creating argument renderer for argument: {arg}, renderer: {renderer_cls.__name__}")
            self.my_pod.arg_renderers.append(renderer_cls(arg))

        excluded_arguments = set()
        for arg_renderer in self.my_pod.arg_renderers:
            excluded_arguments.update(arg_renderer.excludes())

        self.my_pod.in_arg_renderers = [
            arg_renderer
            for arg_renderer in self.my_pod.arg_renderers
            if arg_renderer.arg.name not in excluded_arguments
        ]

        logger.debug(f"in arguments: {self.my_pod.in_arg_renderers}")

        out_args = [arg.name for arg in node.args if arg.is_out]
        self.my_pod.out_args = out_args
        self.my_pod.has_out_args = len(out_args) > 0

    def create_return_renderer(self):
        node = self.node
        return_value = node.returns
        facade_kind = (
            return_value.type.facade.kind
            if return_value.type.facade is not None
            else None
        )
        renderer_cls = RETURN_RENDERER_TABLE.get(facade_kind, ReturnRenderer)
        self.my_pod.return_renderer = renderer_cls(return_value)

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
            out // f'{def_call}("{pyname}", []({self_arg}'
            self.my_pod.render_input()
            out << ")" << out.nl

            with out:
                out("{")
                with out:
                    for arg_renderer in self.my_pod.arg_renderers:
                        arg_renderer.render()

                    self.my_pod.return_renderer.render()

                out("}")
        else:
            out(f'{def_call}("{pyname}", {cname}')

        with out:
            self.render_pyargs()
            out(f", {self.get_return_policy(cursor)})")

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

    def get_return_policy(self, cursor: cindex.Cursor) -> str:
        result = cursor.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"

    def arg_types(self, arguments: List[Argument]):
        return ", ".join([a.type.spelling for a in arguments])

    def arg_name(self, argument: Argument):
        arg_spelling = argument.name
        if argument.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{arg_spelling}[0]"
        return arg_spelling

    def render_pyargs(self):
        for arg_renderer in self.my_pod.in_arg_renderers:
            arg_renderer.render_pyarg()
