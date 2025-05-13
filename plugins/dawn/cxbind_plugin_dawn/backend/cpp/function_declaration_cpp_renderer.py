from ...node import ObjectType, StructureType, EnumType, BitmaskType, NativeType, CallbackInfoType

from ..function_declaration_renderer import FunctionDeclarationRenderer


class FunctionDeclarationCppRenderer(FunctionDeclarationRenderer):
    def render(self):
        fn = self.node
        fn_name = fn.name.CamelCase()
        if fn.returns:
            return_type = self.context.root[fn.returns]
        else:
            return_type = self.context.root['void']

        if return_type.name.native:
            return_type_name = return_type.name.get()
        else:
            return_type_name = return_type.name.CamelCase()

        args = fn.args or []

        arg_list = []
        call_arg_list = []

        for arg in args:
            arg_type = self.context.root[arg.type]
            if arg_type.name.native:
                arg_type_name = arg_type.name.get()
            else:
                arg_type_name = arg_type.name.CamelCase()

            arg_annotation = arg.annotation
            arg_annotation_str = " " + arg.annotation + " " if arg_annotation else " "

            arg_name = arg.name.camelCase()

            arg_list.append(f'{arg_type_name}{arg_annotation_str}{arg_name}')

            if isinstance(arg_type, EnumType) or isinstance(arg_type, BitmaskType):
                if arg.annotation:
                    call_arg_list.append(f"reinterpret_cast<WGPU{arg_type_name}{arg_annotation_str}>({arg_name})")
                else:
                    call_arg_list.append(f"static_cast<WGPU{arg_type_name}{arg_annotation_str}>({arg_name})")
            elif isinstance(arg_type, CallbackInfoType):
                call_arg_list.append(f"*reinterpret_cast<WGPU{arg_type_name}{arg_annotation_str}>({arg_name})")
            elif isinstance(arg_type, StructureType):
                call_arg_list.append(f"reinterpret_cast<WGPU{arg_type_name}{arg_annotation_str}>({arg_name})")
            elif isinstance(arg_type, ObjectType):
                if arg.annotation:
                    call_arg_list.append(f"reinterpret_cast<WGPU{arg_type_name}{arg_annotation_str}>({arg_name})")
                else:
                    call_arg_list.append(f"{arg_name}.Get()")
            else:
                call_arg_list.append(arg_name)

        arg_str = ', '.join(arg_list)
        call_arg_str = ', '.join(call_arg_list)
        call_arg_str = call_arg_str if call_arg_str else 'Get()'
        
        self.out << f"{return_type_name} {fn_name} ({arg_str if arg_list else ''}) {{" << "\n"

        self.out.indent()

        if return_type_name == 'void':
            self.out << f"wgpu{fn_name}({call_arg_str});" << "\n"

        else:
            self.out << f"auto result = wgpu{fn_name}({call_arg_str});" << "\n"
            if isinstance(return_type, ObjectType):
                self.out << f"return {return_type_name}::Acquire(result);" << "\n"
            elif isinstance(return_type, EnumType) or isinstance(return_type, BitmaskType):
                self.out << f"return static_cast<{return_type_name}>(result);" << "\n"
            else:
                #self.out << f"return result;" << "\n"
                exit()
                if return_type_name == "Future":
                    self.out << f"return {return_type_name}{{result.id}});" << "\n"
                else:
                    self.out << f"return result;" << "\n"

        self.out.dedent()

        self.out << "}" << "\n"
