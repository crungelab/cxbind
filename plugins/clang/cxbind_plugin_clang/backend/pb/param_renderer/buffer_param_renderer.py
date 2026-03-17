from loguru import logger

from cxbind.facade import BufferFacade

from ....node import Parameter

from .param_renderer import FacadeParamRenderer


class BufferParamRenderer(FacadeParamRenderer[BufferFacade]):
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.length_param = self.facade.length_param

    def make_facade_type(self):
        if self.param.optional or self.param.default is not None:
            return f"std::optional<py::buffer>"
        else:
            return "py::buffer"

    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        info_name = f"{self.param.name.camelCase()}Info"

        size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"

        logger.debug(
            f"BufferArgWrapper: {self.param.name} type: {self.param.type.spelling.get()} size_expr: {size_expr}"
        )

        if self.param.optional or self.param.default is not None:
            value = f"""\
            py::buffer_info {info_name} = {param_name}.has_value() ? {param_name}.value().request() : py::buffer_info();
            {param_type} {self.param.annotation} _{param_name} = ({param_type} {self.param.annotation}){info_name}.ptr;
            auto {self.length_param.name.camelCase()} = {size_expr};
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {param_name}.request();
            {param_type} {self.param.annotation} _{param_name} = ({param_type} {self.param.annotation}){info_name}.ptr;
            auto {self.length_param.name.camelCase()} = {size_expr};
            """

        out(value)
