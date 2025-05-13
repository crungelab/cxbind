from ..object_type_renderer import ObjectTypeRenderer


class ObjectTypeHppRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()
        self.out(f"""class {class_name} : public ObjectBase<{class_name}, WGPU{class_name}> {{
public:
    using ObjectBase::ObjectBase;
    using ObjectBase::operator=;
""")
        self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(method):
                continue
            method_name = method.name.CamelCase()
            return_type = None
            if method.returns:
                return_name = self.context.root[method.returns].name
                if return_name.native:
                    return_type = return_name.get()
                else:
                    return_type = return_name.CamelCase()
            else:
                return_type = 'void'
            args = method.args or []

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

            self.out << f"{return_type} {method_name}({arg_str if arg_list else ''}) const;" << "\n"

        self.out(f"""
friend ObjectBase<{class_name}, WGPU{class_name}>;
static void WGPUAddRef(WGPU{class_name} handle);
static void WGPURelease(WGPU{class_name} handle);""")
        self.out.dedent()
        self.out << "};" << "\n\n"
