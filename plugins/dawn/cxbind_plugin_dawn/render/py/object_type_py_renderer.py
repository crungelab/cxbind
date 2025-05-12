from ...node import Method
from ..object_type_renderer import ObjectTypeRenderer

class ObjectTypePyRenderer(ObjectTypeRenderer):
    def exclude_method(self, method: Method):
        if method.name.get() == "wait any":
            return True

        return super().exclude_method(method)

    def render(self):
        class_name = self.node.name.CamelCase()

        self.out << f"PYCLASS_BEGIN(m, pywgpu::{class_name}, {class_name}) {class_name}" << "\n"
        self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(method):
                continue

            method_name = method.name.snake_case()
            method_cpp_name = method.name.CamelCase()
            return_type = method.returns
            args = method.args or []

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
                default_value = self.render_cpp_default_value(arg, False, False)

                py_arg_list.append(f'py::arg("{py_arg_name}"){default_value}')
                '''
                if arg.optional:
                    #py_arg_list.append(f'py::arg("{py_arg_name}") = nullptr')
                    py_arg_list.append(f'py::arg("{py_arg_name}") = {default_value}')
                else:
                    py_arg_list.append(f'py::arg("{py_arg_name}")')
                '''

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
            
            method_signature = f'{return_type} (pywgpu::{class_name}::{method_cpp_name}*)({arg_str})'
            #print(method_signature)
            method_expr = f"&pywgpu::{class_name}::{method_cpp_name}"

            if py_arg_list:
                self.out(f"""\
                .def("{method_name}", {method_expr}
                    , {', '.join(py_arg_list)}
                    , py::return_value_policy::automatic_reference)
                """)
            else:
                self.out(f"""\
                .def("{method_name}", {method_expr}
                    , py::return_value_policy::automatic_reference)
                """)

        self.out << "    ;\n"
        self.out.dedent()
        self.out << f"PYCLASS_END(m, pywgpu::{class_name}, {class_name})" << "\n\n"
