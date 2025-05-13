from ...node import ObjectType, StructureType, EnumType, BitmaskType, NativeType, CallbackInfoType
from ..object_type_renderer import ObjectTypeRenderer


class ObjectTypeCppRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()
        self.out << "\n" << f"// {class_name} implementation" << "\n\n"
        for method in self.node.methods:
            if self.exclude_method(method):
                continue

            method_name = method.name.CamelCase()

            if method.returns:
                return_type = self.context.root[method.returns]
            else:
                return_type = self.context.root['void']

            if return_type.name.native:
                return_type_name = return_type.name.get()
            else:
                return_type_name = return_type.name.CamelCase()

            args = method.args or []

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

                if isinstance(arg_type, NativeType):
                    call_arg_list.append(arg_name)
                elif arg_annotation is None:
                    call_arg_list.append(f"*reinterpret_cast<{self.as_cType(arg_type.name)} const*>(&{arg_name})")
                elif isinstance(arg_type, EnumType) or isinstance(arg_type, BitmaskType):
                    if arg.annotation:
                        call_arg_list.append(f"reinterpret_cast<{self.as_cType(arg_type.name)}{arg_annotation_str}>({arg_name})")
                    else:
                        call_arg_list.append(f"static_cast<{self.as_cType(arg_type.name)}{arg_annotation_str}>({arg_name})")
                elif isinstance(arg_type, CallbackInfoType):
                    call_arg_list.append(f"*reinterpret_cast<{self.as_cType(arg_type.name)}{arg_annotation_str}>({arg_name})")
                elif isinstance(arg_type, StructureType):
                    call_arg_list.append(f"reinterpret_cast<{self.as_cType(arg_type.name)}{arg_annotation_str}>({arg_name})")
                elif isinstance(arg_type, ObjectType):
                    if arg.annotation:
                        call_arg_list.append(f"reinterpret_cast<{self.as_cType(arg_type.name)}{arg_annotation_str}>({arg_name})")
                    else:
                        call_arg_list.append(f"{arg_name}.Get()")
                else:
                    call_arg_list.append(arg_name)

            arg_str = ', '.join(arg_list)
            call_arg_str = ', '.join(call_arg_list)
            call_arg_str = 'Get(), ' + call_arg_str if call_arg_str else 'Get()'
            
            self.out << f"{return_type_name} {class_name}::{method_name} ({arg_str if arg_list else ''}) const {{" << "\n"

            self.out.indent()

            if return_type_name == 'void':
                self.out << f"wgpu{class_name}{method_name}({call_arg_str});" << "\n"

            else:
                self.out << f"auto result = wgpu{class_name}{method_name}({call_arg_str});" << "\n"
                if isinstance(return_type, ObjectType):
                    self.out << f"return {return_type_name}::Acquire(result);" << "\n"
                elif isinstance(return_type, EnumType) or isinstance(return_type, BitmaskType):
                    self.out << f"return static_cast<{return_type_name}>(result);" << "\n"
                else:
                    #self.out << f"return result;" << "\n"
                    if return_type_name == "Future":
                        self.out << f"return {return_type_name}{{result.id}};" << "\n"
                    else:
                        self.out << f"return result;" << "\n"


            self.out.dedent()

            self.out << "}" << "\n"

        self.out << f"""
void {class_name}::WGPUAddRef(WGPU{class_name} handle) {{
    if (handle != nullptr) {{
        wgpu{class_name}AddRef(handle);
    }}
}}
void {class_name}::WGPURelease(WGPU{class_name} handle) {{
    if (handle != nullptr) {{
        wgpu{class_name}Release(handle);
    }}
}}
"""
