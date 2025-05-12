from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationPyRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.snake_case()
        fn_cpp_name = fn.name.CamelCase()
        return_type = fn.returns
        args = fn.args or []

        arg_list = []
        arg_type_list = []
        py_arg_list = []
        for arg in args:
            arg_type_name = self.context.root[arg.type].name
            if arg_type_name.native:
                arg_type = arg_type_name.get()
            else:
                arg_type = arg_type_name.camelCase()

            arg_annotation = arg.annotation

            py_arg_name = arg.name.snake_case()
            arg_name = arg.name.camelCase()
            
            if arg.optional:
                #py_arg_list.append(f'py::arg("{py_arg_name}") = py::none()')
                py_arg_list.append(f'py::arg("{py_arg_name}") = nullptr')
            else:
                py_arg_list.append(f'py::arg("{py_arg_name}")')
            
            if arg_annotation:
                arg_list.append(f'{arg_type} {arg_annotation} {arg_name}')
                arg_type_list.append(f'{arg_type} {arg_annotation}')
            else:
                arg_list.append(f'{arg_type} {arg_name}')
                arg_type_list.append(f'{arg_type}')

        arg_str = ', '.join(arg_list)
        #print(arg_str)
        arg_type_str = ', '.join(arg_type_list)
        py_arg_str = ', '.join(py_arg_list)
        
        fn_signature = f'{return_type} (pywgpu::{fn_cpp_name}*)({arg_str})'
        #print(fn_signature)
        fn_expr = f"&pywgpu::{fn_cpp_name}"

        if py_arg_list:
            self.out << f"""
m.def("{fn_name}", {fn_expr}
    , {', '.join(py_arg_list)}
    , py::return_value_policy::automatic_reference)
"""
        else:
            self.out << f"""
m.def("{fn_name}", {fn_expr}
    , py::return_value_policy::automatic_reference)
"""

        self.out << "    ;\n"
