from loguru import logger

from ...name import Name
from ...node import StructureType, RecordMember
from ..structure_type_renderer import StructureTypeRenderer


class StructureTypeHppRenderer(StructureTypeRenderer):
    def exclude_member(self, member: RecordMember) -> bool:
        if self.node.chained:
            if member.name.get() == "next in chain":
                return True
        return super().exclude_member(member)
    
    def render(self):
        node: StructureType = self.node
        struct_name = node.name.CamelCase()
        Out = "Out" if node.output else ""
        const = "const" if not node.output else ""

        if node.chained:
            for chain_root in node.chain_roots:
                self.out(f"// Can be chained in {self.as_cppType(Name.intern(chain_root))}")

            self.out(f"""\
            struct {self.as_cppType(self.node.name)} : ChainedStruct{Out} {{
                {self.as_cppType(node.name)}();

                struct Init;
                {self.as_cppType(node.name)}(Init&& init);""")
        else:
            self.out << f"struct {struct_name} {{" << "\n"
            if node.has_free_members_function:
                self.out(f"{self.as_cppType(node.name)}() = default;")

        self.out.indent()


        if node.has_free_members_function:
            self.out(f"""\
            ~{struct_name}();
            {struct_name}(const {struct_name}&) = delete;
            void FreeMembers();
            {struct_name}& operator=(const {struct_name}&) = delete;
            {struct_name}({struct_name}&&);
            {struct_name}& operator=({struct_name}&&);
            """)

        self.out(f"operator const {self.as_cType(node.name)}&() const noexcept;")

        #if node.extensible and node.extensible == "in":
        '''
        if node.extensible:
            self.out(f"ChainedStruct{Out} {const} * nextInChain = nullptr;")
        '''

        '''
        {% if type.name.get() == "bind group layout entry" %}
            {% if member.name.canonical_case() == "buffer" %}
                {% set forced_default_value = "{ nullptr, BufferBindingType::BindingNotUsed, false, 0 }" %}
            {% elif member.name.canonical_case() == "sampler" %}
                {% set forced_default_value = "{ nullptr, SamplerBindingType::BindingNotUsed }" %}
            {% elif member.name.canonical_case() == "texture" %}
                {% set forced_default_value = "{ nullptr, TextureSampleType::BindingNotUsed, TextureViewDimension::e2D, false }" %}
            {% elif member.name.canonical_case() == "storage texture" %}
                {% set forced_default_value = "{ nullptr, StorageTextureAccess::BindingNotUsed, TextureFormat::Undefined, TextureViewDimension::e2D }" %}
            {% endif %}
        {% endif %}
        '''
        #for member in node.members:
        for i, member in enumerate(node.members):
            if self.exclude_member(member):
                continue
            member_type = self.lookup(member.type)
            forced_default_value = None
            if node.name.get() == "bind group layout entry":
                if member.name.canonical_case() == "buffer":
                    forced_default_value = "{ nullptr, BufferBindingType::BindingNotUsed, false, 0 }"
                elif member.name.canonical_case() == "sampler":
                    forced_default_value = "{ nullptr, SamplerBindingType::BindingNotUsed }"
                elif member.name.canonical_case() == "texture":
                    forced_default_value = "{ nullptr, TextureSampleType::BindingNotUsed, TextureViewDimension::e2D, false }"
                elif member.name.canonical_case() == "storage texture":
                    forced_default_value = "{ nullptr, StorageTextureAccess::BindingNotUsed, TextureFormat::Undefined, TextureViewDimension::e2D }"

            #cppType = self.as_annotated_cppType(member, node.has_free_members_function)
            cppType = self.as_annotated_cppMember(member, node.has_free_members_function)
            #logger.debug(f"cppType: {cppType}")
            default_value = self.render_cpp_default_value(member, True, node.has_free_members_function, forced_default_value)
            #logger.debug(f"default_value: {default_value}")
            member_declaration = f"{cppType}{default_value}"

            if node.chained and i == 1:
                self.out(f"static constexpr size_t kFirstMemberAlignment = detail::ConstexprMax(alignof(ChainedStruct{Out}), alignof({self.decorate_member('', self.as_cppType(member_type.name), member)}));")
                #self.out(f"static constexpr size_t kFirstMemberAlignment = detail::ConstexprMax(alignof(ChainedStruct{Out}), alignof({self.decorate_type(member_type, member)}));")
                self.out(f"alignas(kFirstMemberAlignment) {member_declaration};")
            else:
                self.out(f"{member_declaration};")

        '''
        //* Custom string constructors
        {% if type.name.get() == "string view" %}
            {{wgpu_string_constructors(as_cppType(type.name), false) | indent(4)}}
        {% elif type.name.get() == "nullable string view" %}
            {{wgpu_string_constructors(as_cppType(type.name), true) | indent(4)}}
        {% endif %}
        '''

        if node.name.get() == "string view":
            self.out(self.wgpu_string_constructors(self.as_cppType(node.name), False))
            self.out("operator std::string_view() const;")
        elif node.name.get() == "nullable string view":
            self.out(self.wgpu_string_constructors(self.as_cppType(node.name), True))
            self.out("operator std::optional<std::string_view>() const;")

        '''
            //* Custom string constructors / conversion
            {% if type.name.get() == "string view" %}
                {{wgpu_string_constructors(CppType, false) | indent(8)}}

                // NOLINTNEXTLINE(runtime/explicit) allow implicit conversion
                operator std::string_view() const;
            {% elif type.name.get() == "nullable string view" %}
                {{wgpu_string_constructors(CppType, true) | indent(8)}}

                // NOLINTNEXTLINE(runtime/explicit) allow implicit conversion
                operator std::optional<std::string_view>() const;
            {% endif %}

        '''

        '''
        if node.name.get() == "string view":
            self.out(f"{self.wgpu_string_constructors(self.as_cppType(node.name), False)}")
        elif node.name.get() == "nullable string view":
            self.out(f"{self.wgpu_string_constructors(self.as_cppType(node.name), True)}")
        '''
        self.out.dedent()

        self.out << "};" << "\n\n"