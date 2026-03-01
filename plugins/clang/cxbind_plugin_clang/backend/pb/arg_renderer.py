from typing import Generic, TypeVar

from loguru import logger

from cxbind.facade import ArgFacade, VectorArgFacade, BufferArgFacade

from ...node import Argument

from ..render_context import RenderContext
from ..renderer import Renderer


class ArgRenderer(Renderer):
    def __init__(self, context: RenderContext, arg: Argument):
        super().__init__(context)
        self.arg = arg

    def excludes(self) -> set[str]:
        return set()

    def make_arg_type_string(self):
        arg = self.arg
        arg_type = arg.type
        return arg_type
    
    def make_arg_string(self):
        arg = self.arg
        #arg_type = arg.type
        arg_type = self.make_arg_type_string()
        arg_spelling = arg.name

        if arg_type.endswith("[]"):
            # Remove the array brackets for the argument type
            arg_type = arg_type[:-2]
            # Add the array brackets to the argument spelling
            arg_spelling = f"{arg_spelling}[]"

        return f"{arg_type} {arg_spelling}"

    def make_pass_string(self):
        return self.arg.name

    def make_pyarg_string(self):
        argument = self.arg
        default = f" = {argument.default}" if argument.default else ""
        self.out(f', py::arg("{self.format_field(argument.name)}"){default}')

T_Facade = TypeVar("T_Facade", bound=ArgFacade)

class ArgFacadeRenderer(ArgRenderer, Generic[T_Facade]):
    facade: T_Facade

    def __init__(self, context: RenderContext, arg: Argument):
        super().__init__(context, arg)
        self.facade = arg.spec.facade


class VectorArgWrapper(ArgFacadeRenderer[VectorArgFacade]):
    def __init__(self, context: RenderContext, arg: Argument):
        super().__init__(context, arg)
        self.length_arg = self.facade.length_arg

    def excludes(self) -> set[str]:
        return {self.length_arg}

    def make_arg_type_string(self):
        base_type = self.get_base_type_name(self.arg.cursor.type)
        return f"std::vector<{base_type}>"

    def make_pass_string(self):
        return f"_{super().make_pass_string()}"

    """
    def make_arg_type_string(self):
        arg_type = self.arg.type
        return f"std::vector<{arg_type}>"
    """

    def render(self):
        out = self.out
        arg_name = self.arg.name
        arg_type = self.arg.type
        value = f"""\
        {arg_type} _{arg_name} = ({arg_type}){arg_name}.data();
        auto {self.length_arg} = {arg_name}.size();
        """
        out(value)

'''
class BufferArgRenderer(ArgFacadeRenderer[BufferArgFacade]):
    def __init__(self, context: RenderContext, arg: Argument):
        super().__init__(context, arg)
        self.length_arg = self.facade.length_arg

    def make_facade_type(self):
        if self.arg.optional or self.arg.default_value is not None:
            return f"std::optional<py::buffer>"
        else:
            return "py::buffer"

    # size_t padded_size = (size + 3) & ~size_t(3);

    def render(self):
        arg_name = self.arg.name
        arg_type = get_arg_type_string(self.arg)
        info_name = f"{self.arg.name.camelCase()}Info"

        size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"

        logger.debug(
            f"BufferArgWrapper: {self.arg.name} type: {self.arg.type.name.get()} size_expr: {size_expr}"
        )

        if self.arg.optional or self.arg.default_value is not None:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.has_value() ? {arg_name}.value().request() : py::buffer_info();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_arg.name.camelCase()} = {size_expr};
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.request();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_arg.name.camelCase()} = {size_expr};
            """

        out(value)
    '''

arg_renderer_table = {
    "vector": VectorArgWrapper,
    #"buffer": BufferArgRenderer,
}