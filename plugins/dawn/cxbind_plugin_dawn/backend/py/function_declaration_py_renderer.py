from loguru import logger

from ...name import Name
from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationPyRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.snake_case()
        fn_cpp_name = fn.name.CamelCase()
        #args = fn.args or []

        arg_list = []
        arg_type_list = []
        py_arg_list = []

        args_by_name = {arg.name: arg for arg in fn.args}
        excluded_names = {
            Name.intern(arg.length)
            for arg in fn.args
            if arg.length and isinstance(arg.length, str)
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
            #arg_type_name = self.context.root[arg.type].name
            arg_type_name = arg.type.name
            if arg_type_name.native:
                arg_type = arg_type_name.get()
            else:
                arg_type = arg_type_name.camelCase()

            arg_annotation = arg.annotation

            py_arg_name = arg.name.snake_case()
            arg_name = arg.name.camelCase()
            
            if arg.optional:
                py_arg_list.append(f'py::arg("{py_arg_name}") = nullptr')
            else:
                py_arg_list.append(f'py::arg("{py_arg_name}")')
            
            if arg_annotation:
                arg_list.append(f'{arg_type} {arg_annotation} {arg_name}')
                arg_type_list.append(f'{arg_type} {arg_annotation}')
            else:
                arg_list.append(f'{arg_type} {arg_name}')
                arg_type_list.append(f'{arg_type}')

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
