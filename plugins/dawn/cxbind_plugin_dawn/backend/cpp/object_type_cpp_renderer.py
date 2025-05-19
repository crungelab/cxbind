from ...node import ObjectType, StructureType, EnumType, BitmaskType, NativeType, CallbackInfoType
from ..object_type_renderer import ObjectTypeRenderer


class ObjectTypeCppRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()
        self.out << f"// {class_name} implementation" << "\n\n"
        for method in self.node.methods:
            if self.exclude_method(self.node, method):
                continue

            method_name = method.name.CamelCase()

            return_type = method.return_type
            return_type_name = self.as_cppType(return_type.name)

            args = method.args
            arg_list = []
            call_arg_list = []

            for arg in args:
                arg_type = arg.type
                arg_annotation = arg.annotation
                arg_name = arg.name.camelCase()

                arg_list.append(self.as_annotated_cppMember(arg))
                annotated_type = self.as_annotated_cType(arg)

                if isinstance(arg_type, NativeType):
                    call_arg_list.append(arg_name)
                elif arg_annotation is None:
                    call_arg_list.append(f"*reinterpret_cast<{self.as_cType(arg_type.name)} const*>(&{arg_name})")
                elif isinstance(arg_type, EnumType) or isinstance(arg_type, BitmaskType):
                    if arg.annotation:
                        call_arg_list.append(f"reinterpret_cast<{annotated_type}>({arg_name})")
                    else:
                        call_arg_list.append(f"static_cast<{annotated_type}>({arg_name})")
                elif isinstance(arg_type, CallbackInfoType):
                    call_arg_list.append(f"*reinterpret_cast<{annotated_type}>({arg_name})")
                elif isinstance(arg_type, StructureType):
                    call_arg_list.append(f"reinterpret_cast<{annotated_type}>({arg_name})")
                elif isinstance(arg_type, ObjectType):
                    if arg.annotation:
                        call_arg_list.append(f"reinterpret_cast<{annotated_type}>({arg_name})")
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
                self.out / f"wgpu{class_name}{method_name}({call_arg_str});" << "\n"
            else:
                self.out / f"auto result = wgpu{class_name}{method_name}({call_arg_str});" << "\n"
                if isinstance(return_type, ObjectType):
                    self.out / f"return {return_type_name}::Acquire(result);" << "\n"
                elif isinstance(return_type, EnumType) or isinstance(return_type, BitmaskType):
                    self.out / f"return static_cast<{return_type_name}>(result);" << "\n"
                else:
                    if return_type_name == "Future":
                        self.out / f"return {return_type_name}{{result.id}};" << "\n"
                    else:
                        self.out / f"return result;" << "\n"

            self.out.dedent()

            self.out << "}" << "\n\n"

        self.out(f"""\
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
        """)
