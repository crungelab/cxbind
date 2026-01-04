from loguru import logger

from ...name import Name
from ...node import Method, RecordMember, StructureType

from ..render_stream import RenderStream
from ..renderer import Renderer, T_Node

SpecialStructures = ["string view", "nullable string view"]

def get_arg_type_string(arg) -> str:
    arg_type = ""
    arg_type_name = arg.type.name
    if arg_type_name.native:
        arg_type = arg_type_name.get()
    else:
        arg_type = "pywgpu::" + arg_type_name.CamelCase()
    return arg_type


class ArgWrapper:
    def __init__(self, arg: RecordMember):
        self.arg = arg

    def render(self, out: RenderStream):
        pass

    def make_wrapper_type(self):
        pass


class BufferArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember, length_member: RecordMember):
        super().__init__(arg)
        self.length_member = length_member

    def make_wrapper_type(self):
        if self.arg.optional or self.arg.default_value is not None:
            return f"std::optional<py::buffer>"
        else:
            return "py::buffer"

    # size_t padded_size = (size + 3) & ~size_t(3);

    def render(self, out: RenderStream):
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg)
        info_name = f"{self.arg.name.camelCase()}Info"

        """
        size_expr = f"{info_name}.size * {info_name}.itemsize"

        if self.arg.type.name.get() == "buffer":
            size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"
        """
        size_expr = f"(({info_name}.size * {info_name}.itemsize) + 3) & ~size_t(3)"
        # size_expr = f"{info_name}.size * {info_name}.itemsize"

        logger.debug(
            f"BufferArgWrapper: {self.arg.name} type: {self.arg.type.name.get()} size_expr: {size_expr}"
        )

        if self.arg.optional or self.arg.default_value is not None:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.has_value() ? {arg_name}.value().request() : py::buffer_info();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_member.name.camelCase()} = {size_expr};
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.request();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_member.name.camelCase()} = {size_expr};
            """

        out(value)


class VectorArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember, length_member: RecordMember):
        super().__init__(arg)
        self.length_member = length_member

    def make_wrapper_type(self):
        arg_type = get_arg_type_string(self.arg)
        return f"std::vector<{arg_type}>"

    def render(self, out: RenderStream):
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg)
        value = f"""\
        {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){arg_name}.data();
        auto {self.length_member.name.camelCase()} = {arg_name}.size();
        """
        out(value)


class DescriptorArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember):
        super().__init__(arg)

    def make_wrapper_type(self):
        return f"py::handle"

    def render(self, out: RenderStream):
        logger.debug(f"DescriptorArgWrapper: {self.arg.name} type: {self.arg.type.name.get()}")
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg)
        arg_type_spelling = self.arg.type.name.CamelCase()
        value = f"""\
        {arg_type} {self.arg.annotation} _{arg_name} = Builder<{arg_type_spelling}>(ctx).build({arg_name});
        """
        out(value)


class DescriptorArrayArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember, length_member: RecordMember):
        super().__init__(arg)
        self.length_member = length_member

    def make_wrapper_type(self):
        return f"py::handle"

    def render(self, out: RenderStream):
        logger.debug(f"DescriptorArrayArgWrapper: {self.arg.name} type: {self.arg.type.name.get()}")
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg)
        arg_type_spelling = self.arg.type.name.CamelCase()
        value = f"""\
        uint32_t {self.length_member.name.camelCase()};
        {arg_type} {self.arg.annotation} _{arg_name} = Builder<{arg_type_spelling}>(ctx).build_array({arg_name}, &{self.length_member.name.camelCase()});
        """
        out(value)


class PbFunctionalRenderer(Renderer[T_Node]):
    def is_descriptor_arg(self, arg: RecordMember) -> bool:
        arg_type = arg.type
        if isinstance(arg_type, StructureType) and not arg_type.output and not arg_type.name.get() in SpecialStructures:
            return True
        return False

