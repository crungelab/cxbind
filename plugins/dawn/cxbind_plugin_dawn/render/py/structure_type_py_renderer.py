from loguru import logger

from ...node import FunctionPointerType
from ..structure_type_renderer import StructureTypeRenderer

class StructureTypePyRenderer(StructureTypeRenderer):
    def render(self):
        node = self.node
        class_name = node.name.CamelCase()
        Out = "Out" if node.output else ""
        const = "const" if not node.output else ""

        if node.chained:
            self.out << f"PYSUBCLASS_BEGIN(m, pywgpu::{class_name}, ChainedStruct{Out}, {class_name}) {class_name}" << "\n"
        else:
            self.out << f"PYCLASS_BEGIN(m, pywgpu::{class_name}, {class_name}) {class_name}" << "\n"
        self.out.indent()

        '''
        if node.extensible:
            self.out << f'.def_readwrite("next_in_chain", &pywgpu::{class_name}::nextInChain)' << "\n"
        '''

        for member in node.members:
            if self.exclude_member(member):
                continue

            #member_name = member.name.snake_case()
            member_name = member.name.snake_case().lower()
            member_cpp_name = member.name.camelCase()
            member_type = self.lookup(member.type)
            member_annotation = member.annotation

            if member_annotation == "const*const*":
                logger.debug(f"Skipping const*const* member {member_name}")
                continue

            #logger.debug(f"member_type: {member_type}")
            if isinstance(member_type, FunctionPointerType):
                logger.debug(f"Skipping function pointer member {member_name}")
                continue
                
            readonly = (node.extensible is not None and node.extensible == "out") or (node.chained  is not None and node.chained == "out")
            #def_kind = "def_readonly" if node.extensible and node.extensible == "out" or node.chained and node.chained == "out" else "def_readwrite"
            def_kind = "def_readonly" if readonly else "def_readwrite"
            decoration = self.decorate_member('', self.as_cppType(member_type.name), member)
            #print(decoration)

            if decoration == "char const * " and not readonly:
                #print(decoration, readonly)
                self.out << f'.def_property("{member_name}",' << "\n"
                self.out.indent()
                self.out << f'[](const pywgpu::{class_name}& self) {{' << "\n"
                self.out.indent()
                self.out << f'return self.{member_cpp_name};' << "\n"
                self.out.dedent()
                self.out << '},' << "\n"
                self.out << f'[](pywgpu::{class_name}& self, {decoration} source) {{' << "\n"
                self.out.indent()
                self.out << f'self.{member_cpp_name} = strdup(source);' << "\n"
                self.out.dedent()
                self.out << '}' << "\n"
                self.out.dedent()
                self.out << ')' << "\n"
            else:
                self.out << f'.{def_kind}("{member_name}", &pywgpu::{class_name}::{member_cpp_name})' << "\n"

        self.render_init()

        self.out.dedent()
        self.out << ";\n"
        self.out << f"PYCLASS_END(m, pywgpu::{class_name}, {class_name})" << "\n\n"

    def render_init(self):
        node = self.node
        '''
        if node.output:
            return
        '''
        if node.extensible and node.extensible == "out" or node.chained and node.chained == "out":
            return

        class_name = node.name.CamelCase()

        self.out << f'.def(py::init([](const py::kwargs& kwargs) {{' << "\n"
        self.out.indent()
        #self.out << f'pywgpu::{class_name} obj = {{}};' << "\n"
        self.out << f'pywgpu::{class_name} obj{{}};' << "\n"
        #self.out << f'pywgpu::{class_name} obj;' << "\n"

        '''
        if node.extensible:
            self.out(f"""\
            if (kwargs.contains("next_in_chain"))
            {{
                obj.nextInChain = kwargs["next_in_chain"].cast<const pywgpu::ChainedStruct*>();
            }}
            """)
        '''

        for member in node.members:
            if self.exclude_member(member):
                continue

            member_name = member.name.snake_case().lower()
            member_cpp_name = member.name.camelCase()
            member_type = self.lookup(member.type)
            member_annotation = member.annotation

            if member_annotation == "const*const*":
                logger.debug(f"Skipping const*const* member {member_name}")
                continue

            #logger.debug(f"member_type: {member_type}")
            if isinstance(member_type, FunctionPointerType):
                logger.debug(f"Skipping function pointer member {member_name}")
                continue

            self.out << f'if (kwargs.contains("{member_name}"))' << "\n"
            self.out << "{" << "\n"
            self.out.indent()

            cppType = self.as_annotated_cppType(member, node.has_free_members_function)

            stripped_cppType = cppType.replace("const ", "").replace(" *", "")

            if member.length:
                stripped_cppType = cppType.replace("const ", "").replace(" *", "")
                #print(f"stripped_cppType: {stripped_cppType}")
                if stripped_cppType == "char":
                    self.out << f'auto value = kwargs["{member_name}"].cast<std::string>();' << "\n"
                    self.out << f'obj.{member_cpp_name} = strdup(value.c_str());' << "\n"
                else:
                    self.out << f'auto _value = kwargs["{member_name}"].cast<std::vector<{stripped_cppType}>>();' << "\n"
                    self.out << f'auto count = _value.size();' << "\n"
                    self.out << f'auto value = new {stripped_cppType}[count];' << "\n"
                    #self.out << f'obj.{member_cpp_name} = new {stripped_cppType}[count];' << "\n"
                    self.out << f'std::copy(_value.begin(), _value.end(), value);' << "\n"
                    self.out << f'obj.{member_cpp_name} = value;' << "\n"
            else:
                self.out << f'auto value = kwargs["{member_name}"].cast<{cppType}>();' << "\n"
                self.out << f'obj.{member_cpp_name} = value;' << "\n"

            self.out.dedent()
            self.out << "}" << "\n"
        self.out << "return obj;" << "\n"
        self.out.dedent()
        self.out << "}), py::return_value_policy::automatic_reference)" << "\n"
