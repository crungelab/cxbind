from typing import TypeVar

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec
from cxbind.facade import Facade

from ...node import FunctionalNode, Parameter

from .node_renderer import NodeRenderer, RenderContext
from .param_renderer import ParamRenderer, PARAM_RENDERER_TABLE
from .return_renderer import ReturnRenderer, RETURN_RENDERER_TABLE
from .functional_render_pod import FunctionalRenderPod

T_Node = TypeVar("T_Node", bound=FunctionalNode)


class FunctionalRenderer(NodeRenderer[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__(node)
        self.node = node
        self._pod = FunctionalRenderPod(node)
        self.create_param_renderers()
        self.create_return_renderer()

    @property
    def pod(self) -> FunctionalRenderPod:
        return self._pod

    def create_param_renderers(self):
        node = self.node
        logger.debug(f"Creating parameter renderers for node: {node.name}")
        logger.debug(f"Node parameters: {node.params}")

        for param in node.params:
            facade_kind = (
                param.type.facade.kind if param.type.facade is not None else None
            )
            renderer_cls = PARAM_RENDERER_TABLE.get(facade_kind, ParamRenderer)
            logger.debug(
                f"Creating parameter renderer for parameter: {param}, renderer: {renderer_cls.__name__}"
            )
            self.pod.arg_renderers.append(renderer_cls(param))

        excluded_params = set()
        for arg_renderer in self.pod.arg_renderers:
            excluded_params.update(arg_renderer.excludes())

        self.pod.param_renderers = [
            arg_renderer
            for arg_renderer in self.pod.arg_renderers
            if arg_renderer.param.name not in excluded_params
        ]

        logger.debug(f"param_renderers: {self.pod.param_renderers}")

        out_params = [param.name for param in node.params if param.is_out]
        self.pod.out_params = out_params
        self.pod.has_out_params = len(out_params) > 0

    def create_return_renderer(self):
        node = self.node
        return_value = node.returns
        facade_kind = (
            return_value.type.facade.kind
            if return_value.type.facade is not None
            else None
        )
        renderer_cls = RETURN_RENDERER_TABLE.get(facade_kind, ReturnRenderer)
        self.pod.return_renderer = renderer_cls(return_value)

    def render(self):
        self.pod.make_current()

        out = self.out
        node = self.node
        cursor = node.cursor
        params = node.params
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
            cname = f"py::overload_cast<{self.param_types(params)}>({cname}{extra})"

        if self.should_wrap_function():
            is_non_static_method = (
                cursor.kind == cindex.CursorKind.CXX_METHOD
                and not cursor.is_static_method()
            )
            self_arg = f"{self.top_node.name}& self, " if is_non_static_method else ""
            out // f'{def_call}("{pyname}", []({self_arg}'
            self.pod.render_params()
            out << ")" << out.nl

            with out:
                out("{")
                with out:
                    for arg_renderer in self.pod.arg_renderers:
                        arg_renderer.render()

                    self.pod.return_renderer.render()

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

        result_type = node.returns.type.type
        if self.is_wrapped_type(result_type):
            return True

        for param in node.params:
            param_type = param.type.type

            if param_type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True

            if param.is_out:
                logger.debug(
                    f"Found out parameter in function {node.cursor.spelling}, parameter {param.name}"
                )
                return True

            if self.is_wrapped_type(param_type):
                return True

            if param.spec is not None and param.spec.facade is not None:
                return True

        return False

    def get_return_policy(self, cursor: cindex.Cursor) -> str:
        result = cursor.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"

    def param_types(self, params: list[Parameter]):
        return ", ".join([param.type.spelling for param in params])

    def param_name(self, param: Parameter):
        param_name = param.name
        if param.cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{param_name}[0]"
        return param_name

    def render_pyargs(self):
        for arg_renderer in self.pod.param_renderers:
            arg_renderer.render_pyarg()
