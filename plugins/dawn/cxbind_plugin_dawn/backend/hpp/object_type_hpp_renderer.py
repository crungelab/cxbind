from ..object_type_renderer import ObjectTypeRenderer


class ObjectTypeHppRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()
        self.out(f"""\
        class {class_name} : public ObjectBase<{class_name}, WGPU{class_name}> {{
        public:
            using ObjectBase::ObjectBase;
            using ObjectBase::operator=;
        """)
        self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(self.node, method):
                continue
            method_name = method.name.CamelCase()

            return_type = method.return_type
            return_type_name = self.as_cppType(return_type.name)

            arg_list = []

            for arg in method.args:
                arg_list.append(self.as_annotated_cppMember(arg))

            arg_str = ', '.join(arg_list)

            self.out / f"{return_type_name} {method_name}({arg_str if arg_list else ''}) const;" << "\n"

        self.out(f"""\
        friend ObjectBase<{class_name}, WGPU{class_name}>;
        static void WGPUAddRef(WGPU{class_name} handle);
        static void WGPURelease(WGPU{class_name} handle);\
        """)
        self.out.dedent()
        self.out << "};" << "\n\n"
