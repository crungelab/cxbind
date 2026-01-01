from loguru import logger

from ...name import Name
from ...node import Method, RecordMember

from ..render_stream import RenderStream
from ..object_type_renderer import ObjectTypeRenderer, ObjectType


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


'''
    def render(self, out: RenderStream):
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg)
        info_name = f"{self.arg.name.camelCase()}Info"

        if self.arg.optional or self.arg.default_value is not None:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.has_value() ? {arg_name}.value().request() : py::buffer_info();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_member.name.camelCase()} = {info_name}.size * {info_name}.itemsize;
            """
        else:
            value = f"""\
            py::buffer_info {info_name} = {arg_name}.request();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_member.name.camelCase()} = {info_name}.size * {info_name}.itemsize;
            """

        out(value)
'''


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


class ObjectTypePbRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()

        (
            self.out
            << f'py::class_<{class_name}> _{class_name}(m, "{class_name}");'
            << "\n"
        )
        self.out / f'registry.on(m, "{class_name}", _{class_name});' << "\n\n"
        self.out / f"_{class_name}" << "\n"

        self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(self.node, method):
                continue

            method_name = method.name.snake_case()
            if method.return_type.name.get() == "future":
                method_name = "_" + method_name

            method_cpp_name = method.name.CamelCase()
            use_lambda = False

            excluded_names = {
                arg.length_member.name
                for arg in method.args
                if arg.length_member is not None
            }

            if excluded_names:
                use_lambda = True

            args = [arg for arg in method.args if arg.name not in excluded_names]

            arg_list = []
            py_arg_list = []
            snippet_list = []
            arg_wrappers = {}

            for arg in args:
                if arg.length_member is not None:
                    arg_type = arg.type
                    arg_wrapper = None
                    if arg_type.name.native:
                        arg_wrapper = BufferArgWrapper(arg, arg.length_member)
                    else:
                        arg_wrapper = VectorArgWrapper(arg, arg.length_member)
                    arg_wrappers[arg.name] = arg_wrapper

                    snippet_list.append(arg_wrapper)

            for arg in args:
                arg_type = get_arg_type_string(arg)
                py_arg_name = arg.name.snake_case()
                default_value = self.render_cpp_default_value(arg, False, False)

                py_arg_list.append(f'py::arg("{py_arg_name}"){default_value}')

                if arg.name in arg_wrappers:
                    arg_list.append(
                        f"{arg_wrappers[arg.name].make_wrapper_type()} {arg.name.camelCase()}"
                    )
                else:
                    arg_list.append(self.as_annotated_cppMember(arg))

            arg_name_list = []

            for arg in method.args:
                if arg.name in arg_wrappers:
                    arg_name_list.append(f"_{arg.name.camelCase()}")
                else:
                    arg_name_list.append(f"{arg.name.camelCase()}")

            self.out / f'.def("{method_name}",'
            self.out.indent()

            if use_lambda:
                (
                    self.out
                    << f"[](pywgpu::{class_name}& self, {', '.join(arg_list)}) {{"
                    << "\n"
                )
                for snippet in snippet_list:
                    snippet.render(self.out)
                (
                    self.out
                    / f"return self.{method_cpp_name}({', '.join(arg_name_list)});"
                    << "\n"
                )
                self.out / "}" << "\n"

            else:
                self.out << f"&pywgpu::{class_name}::{method_cpp_name}" << "\n"

            if py_arg_list:
                self.out(
                    f"""\
                , {', '.join(py_arg_list)}
                , py::return_value_policy::automatic_reference)
                """
                )
            else:
                self.out(
                    f"""\
                , py::return_value_policy::automatic_reference)
                """
                )

            self.out.dedent()

        self.out / ";\n"
        self.out.dedent()
        self.out << "\n"
