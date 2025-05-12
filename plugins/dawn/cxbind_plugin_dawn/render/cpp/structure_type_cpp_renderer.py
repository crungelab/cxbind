from ...node import RecordMember

from ..structure_type_renderer import StructureTypeRenderer


class StructureTypeCppRenderer(StructureTypeRenderer):
    def exclude_member(self, member: RecordMember) -> bool:
        if self.node.chained:
            if member.name.get() == "next in chain":
                return True
        return super().exclude_member(member)

    def render(self):
        node = self.node
        struct_name = node.name.CamelCase()

        self.out(f"""\
        // {struct_name} implementation

        {struct_name}::operator const {self.as_cType(node.name)}&() const noexcept {{
            return *reinterpret_cast<const {self.as_cType(node.name)}*>(this);
        }}
        """)
        
        if node.chained:
            Out = "Out" if node.output else ""
            const = "const" if not node.output else ""

            self.out(f"""\
            {struct_name}::{struct_name}()
            : ChainedStruct{Out} {{ nullptr, SType::{struct_name} }} {{}}
            """)
            
            '''
            self.out(f"""\
            struct {struct_name}::Init {{
                ChainedStruct{Out} * {const} nextInChain;""")
            '''
            self.out(f"struct {struct_name}::Init {{")

            self.out.indent()
            for member in node.members:
                '''
                if self.exclude_member(member):
                    continue
                '''
                member_declaration = self.as_annotated_cppMember(member, node.has_free_members_function)  + self.render_cpp_default_value(member, True, node.has_free_members_function)
                self.out(f"{member_declaration};")
            self.out.dedent()
            self.out("};")

            self.out(f"""\
            {struct_name}::{struct_name}({struct_name}::Init&& init)
            : ChainedStruct{Out} {{ init.nextInChain, SType::{struct_name} }}""")
            self.out.indent()
            for member in node.members:
                if self.exclude_member(member):
                    continue

                self.out(f",{self.as_varName(member.name)}(std::move(init.{self.as_varName(member.name)}))")
            self.out(" {}")
            self.out.dedent()

                     
        #elif node.has_free_members_function:
        #    self.out << f"{struct_name}::{struct_name}() = default;" << "\n"
            
        if node.has_free_members_function:
            self.out(f"""\
            {struct_name}::~{struct_name}() {{
                FreeMembers();
            }}
            void {struct_name}::FreeMembers() {{
                // Free members here
            }}
            """)

            self.out << f"{struct_name}::{struct_name}({struct_name}&& rhs) :" << "\n"
            self.out.indent()
            for i, member in enumerate(node.members):
                if self.exclude_member(member):
                    continue

                comma = "" if i == len(node.members) - 1  else ","
                member_name = member.name.camelCase()
                self.out << f"{member_name}(rhs.{member_name}){comma}" << "\n"
            self.out.dedent()
            self.out << "{}" << "\n"

            '''
            self.out << f"{struct_name}::{struct_name}({struct_name}&& rhs) {{" << "\n"
            self.out.indent()
            for member in node.members:
                member_name = member.name.camelCase()
                self.out << f"{member_name}(rhs.{member_name});" << "\n"
            self.out.dedent()
            self.out << "}" << "\n"
            '''

            self.out(f"""\
            {struct_name}& {struct_name}::operator=({struct_name}&& rhs) {{
            if (&rhs == this) {{
                return *this;
            }}
            FreeMembers();
            """)
            
            self.out.indent()
            for member in node.members:
                if self.exclude_member(member):
                    continue

                member_name = member.name.camelCase()
                #this->{{member.name.camelCase()}} = std::move(rhs.{{member.name.camelCase()}});
                #self.out << f"{member_name} = rhs.{member_name};" << "\n"
                #self.out << f"this->{member_name} = std::move(rhs.{member_name});" << "\n"
                self.out << f"::pywgpu::detail::AsNonConstReference(this->{member_name}) = std::move(rhs.{member_name});" << "\n"


            self.out << "return *this;" << "\n"
            self.out.dedent()
            self.out << "}" << "\n"