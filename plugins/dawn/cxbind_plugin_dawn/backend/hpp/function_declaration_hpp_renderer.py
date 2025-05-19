from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationHppRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.CamelCase()

        return_type = fn.return_type
        return_type_name = self.as_cppType(return_type.name)

        arg_list = []

        for arg in fn.args:
            arg_list.append(self.as_annotated_cppMember(arg))

        arg_str = ', '.join(arg_list)

        self.out << f"{return_type_name} {fn_name}({arg_str if arg_list else ''});" << "\n"