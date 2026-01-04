from loguru import logger

from ...name import Name
from ...node import Method, RecordMember, StructureType, ObjectType

from ..render_stream import RenderStream
from ..renderer import Renderer, T_Node

from .pb_render_context import PbRenderContext
from .pb_functional_renderer import (
    PbFunctionalRenderer,
    get_arg_type_string,
    ArgWrapper,
    BufferArgWrapper,
    VectorArgWrapper,
    DescriptorArgWrapper,
    SpecialStructures,
)


class PbMethodRenderer(PbFunctionalRenderer[Method]):
    def __init__(self, context: PbRenderContext, node: Method, object_type: ObjectType):
        super().__init__(context, node)
        self.object_type = object_type

    def render(self):
        method = self.node
        class_name = self.object_type.name.CamelCase()

        method_name = method.name.snake_case()
        if method.return_type.name.get() == "future":
            method_name = "_" + method_name

        method_cpp_name = method.name.CamelCase()
        use_lambda = False
        use_builders = False

        excluded_names = {
            arg.length_member.name
            for arg in method.args
            if arg.length_member is not None
        }

        if excluded_names:
            use_lambda = True
            logger.debug(
                #f"Method '{method_name}' has excluded names: {', '.join(excluded_names)}"
                f"Method '{method_name}' has excluded names: {excluded_names}"
            )

        args = [arg for arg in method.args if arg.name not in excluded_names]

        arg_list = []
        py_arg_list = []
        snippet_list = []
        arg_wrappers = {}

        for arg in args:
            arg_wrapper = None
            arg_type = arg.type
            arg_type_name = arg_type.name

            #if isinstance(arg_type, StructureType) and not arg_type.output and not arg_type_name.get() in SpecialStructures:
            if self.is_descriptor_arg(arg):
                logger.debug(
                    f"Descriptor arg detected: {arg.name} of type {arg.type.name.get()}"
                )
                arg_wrapper = DescriptorArgWrapper(arg)
                arg_wrappers[arg.name] = arg_wrapper
                snippet_list.append(arg_wrapper)
                use_lambda = True
                use_builders = True

            elif arg.length_member is not None:
                # arg_type = arg.type
                # arg_wrapper = None
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
            if use_builders:
                self.out("""
                LinearAlloc la;
                BuildCtx ctx{la};
                """)
            for snippet in snippet_list:
                snippet.render(self.out)
            (
                self.out / f"return self.{method_cpp_name}({', '.join(arg_name_list)});"
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
