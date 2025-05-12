from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationHppRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.CamelCase()
        return_type = None
        if fn.returns:
            return_name = self.context.root[fn.returns].name
            if return_name.native:
                return_type = return_name.get()
            else:
                return_type = return_name.CamelCase()
        else:
            return_type = 'void'
        args = fn.args or []

        arg_list = []
        arg_type_list = []
        for arg in args:
            arg_type_name = self.context.root[arg.type].name
            if arg_type_name.native:
                arg_type = arg_type_name.get()
            else:
                arg_type = arg_type_name.CamelCase()

            arg_annotation = arg.annotation

            arg_name = arg.name.camelCase()
            
            if arg_annotation:
                arg_list.append(f'{arg_type} {arg_annotation} {arg_name}')
                arg_type_list.append(f'{arg_type} {arg_annotation}')
            else:
                arg_list.append(f'{arg_type} {arg_name}')
                arg_type_list.append(f'{arg_type}')

        arg_str = ', '.join(arg_list)

        self.out << f"{return_type} {fn_name}({arg_str if arg_list else ''});" << "\n"