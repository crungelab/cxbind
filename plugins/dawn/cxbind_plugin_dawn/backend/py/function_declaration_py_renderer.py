from loguru import logger

from ...name import Name
from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationPyRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.snake_case()
        fn_cpp_name = fn.name.CamelCase()

        arg_list = []
        arg_type_list = []
        py_arg_list = []

        excluded_names = {
            arg.length_member.name
            for arg in fn.args
            if arg.length_member is not None
        }

        if excluded_names:
            logger.debug(
                f"Function '{fn_name}' has excluded names: {', '.join(excluded_names)}"
            )
            exit()

        args = [
            arg
            for arg in fn.args
            if arg.name not in excluded_names
        ]

        for arg in args:
            py_arg_name = arg.name.snake_case()
            
            if arg.optional:
                py_arg_list.append(f'py::arg("{py_arg_name}") = nullptr')
            else:
                py_arg_list.append(f'py::arg("{py_arg_name}")')

            arg_list.append(self.as_annotated_cppMember(arg))
            arg_type_list.append(self.as_annotated_cppType(arg))

        fn_expr = f"&pywgpu::{fn_cpp_name}"

        if py_arg_list:
            self.out(f"""\
            m.def("{fn_name}", {fn_expr}
                , {', '.join(py_arg_list)}
                , py::return_value_policy::automatic_reference)\
            """)
        else:
            self.out(f"""\
            m.def("{fn_name}", {fn_expr}
                , py::return_value_policy::automatic_reference)\
            """)

        self.out << ";\n\n"
