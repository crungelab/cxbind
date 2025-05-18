from loguru import logger

from ...name import Name
from ...node import Method, RecordMember

from ..object_type_renderer import ObjectTypeRenderer, ObjectType

def get_arg_type_string(arg, context):
    arg_type = ""
    arg_type_name = context.root[arg.type].name
    if arg_type_name.native:
        arg_type = arg_type_name.get()
    else:
        arg_type = "pywgpu::" + arg_type_name.CamelCase()
    return arg_type


class ArgWrapper:
    def __init__(self, arg: RecordMember):
        self.arg = arg

    def make_snippet(self, context):
        pass

    def make_wrapper_type(self, context):
        pass

class BufferArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember, length_member: RecordMember):
        super().__init__(arg)
        self.length_member = length_member

    def make_wrapper_type(self, context):
        return "py::buffer"
    
    def make_snippet(self, context):
        value = ""
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg, context)
        if self.arg.length is not None and isinstance(self.arg.length, str):
            info_name = f"{self.arg.name.camelCase()}Info"
            value = f"""
            py::buffer_info {info_name} = {arg_name}.request();
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){info_name}.ptr;
            auto {self.length_member.name.camelCase()} = {info_name}.size * {info_name}.itemsize;
            """
        return value

class VectorArgWrapper(ArgWrapper):
    def __init__(self, arg: RecordMember, length_member: RecordMember):
        super().__init__(arg)
        self.length_member = length_member

    def make_wrapper_type(self, context):
        arg_type = get_arg_type_string(self.arg, context)
        #cppType = f"{arg_type} {self.arg.annotation}"
        #stripped_cppType = cppType.replace("const ", "").replace(" *", "")
        #return f"std::vector<{stripped_cppType}>"
        return f"std::vector<{arg_type}>"

    def make_snippet(self, context):
        value = ""
        arg_name = self.arg.name.camelCase()
        arg_type = get_arg_type_string(self.arg, context)
        if self.arg.length is not None and isinstance(self.arg.length, str):
            value = f"""
            {arg_type} {self.arg.annotation} _{arg_name} = ({arg_type} {self.arg.annotation}){arg_name}.data();
            auto {self.length_member.name.camelCase()} = {arg_name}.size();
            """
        return value


class ObjectTypePyRenderer(ObjectTypeRenderer):
    def exclude_method(self, object_type: ObjectType, method: Method):
        if method.name.get() == "wait any":
            return True

        return super().exclude_method(object_type, method)

    def render(self):
        class_name = self.node.name.CamelCase()

        self.out << f"PYCLASS_BEGIN(m, pywgpu::{class_name}, {class_name}) {class_name}" << "\n"
        self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(self.node, method):
                continue

            method_name = method.name.snake_case()
            method_cpp_name = method.name.CamelCase()
            return_type = method.returns
            #args = method.args or []
            use_lambda = False

            args_by_name = {arg.name: arg for arg in method.args}
            excluded_names = {
                Name.intern(arg.length)
                for arg in method.args
                if arg.length and isinstance(arg.length, str)
            }

            if excluded_names:
                use_lambda = True

            args = [
                arg
                for arg in method.args
                if arg.name not in excluded_names
            ]

            arg_list = []
            arg_type_list = []
            py_arg_list = []
            substition_list = []
            arg_wrappers = {}


            for arg in args:
                if arg.length is not None and isinstance(arg.length, str):
                    arg_type = self.lookup(arg.type)
                    length_member = args_by_name[Name.intern(arg.length)]
                    #arg_wrappers[arg.name] = ArgWrapper(arg, "py::buffer")
                    arg_wrapper = None
                    if arg_type.name.native:
                        arg_wrapper = BufferArgWrapper(arg, length_member)
                    else:
                        arg_wrapper = VectorArgWrapper(arg, length_member)
                    arg_wrappers[arg.name] = arg_wrapper

                    #substition_list.append(f'auto {length_member.name.camelCase()} = {arg_name}->size()')
                    substition_list.append(arg_wrapper.make_snippet(self.context))

            for arg in args:
                '''
                arg_type_name = self.context.root[arg.type].name
                if arg_type_name.native:
                    arg_type = arg_type_name.get()
                else:
                    #arg_type = arg_type_name.camelCase()
                    arg_type = "pywgpu::" + arg_type_name.CamelCase()
                '''
                arg_type = get_arg_type_string(arg, self.context)
                arg_annotation = arg.annotation

                py_arg_name = arg.name.snake_case()
                arg_name = arg.name.camelCase()
                default_value = self.render_cpp_default_value(arg, False, False)

                py_arg_list.append(f'py::arg("{py_arg_name}"){default_value}')

                if arg.name in arg_wrappers:
                    arg_list.append(f"{arg_wrappers[arg.name].make_wrapper_type(self.context)} {arg.name.camelCase()}")
                elif arg_annotation:
                    arg_list.append(f'{arg_type} {arg_annotation} {arg_name}')
                    arg_type_list.append(f'{arg_type} {arg_annotation}')
                else:
                    arg_list.append(f'{arg_type} {arg_name}')
                    arg_type_list.append(f'{arg_type}')

                '''
                if arg.length is not None and isinstance(arg.length, str):
                    length_member = args_by_name[Name.intern(arg.length)]
                    #arg_wrappers[arg.name] = ArgWrapper(arg, "py::buffer")
                    arg_wrapper = BufferArgWrapper(arg, length_member)
                    arg_wrappers[arg.name] = arg_wrapper

                    #substition_list.append(f'auto {length_member.name.camelCase()} = {arg_name}->size()')
                    substition_list.append(arg_wrapper.snippet())
                '''


            arg_name_list = []
            for arg in method.args:
                if arg.name in arg_wrappers:
                    arg_name_list.append(f"_{arg.name.camelCase()}")
                else:
                    arg_name_list.append(f"{arg.name.camelCase()}")

            substition_snippet = ";\n".join(substition_list)

            lambda_arg_list = []
            for arg in args:
                if arg.name in arg_wrappers:
                    lambda_arg_list.append(f"{arg_wrappers[arg.name].make_wrapper_type(self.context)} {arg.name.camelCase()}")
                else:
                    lambda_arg_list.append(f"{arg.name.camelCase()}")

            if use_lambda:
                method_expr = f"""[](pywgpu::{class_name}& self, {', '.join(arg_list)}) {{
                        {substition_snippet}
                        return self.{method_cpp_name}({', '.join(arg_name_list)});
                    }}"""
            else:
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
