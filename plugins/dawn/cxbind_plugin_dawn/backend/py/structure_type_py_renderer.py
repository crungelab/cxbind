from loguru import logger

from ...name import Name
from ...node import FunctionPointerType, StructureType, EnumType, BitmaskType
from ..structure_type_renderer import StructureTypeRenderer


class StructureTypePyRenderer(StructureTypeRenderer):
    def render(self):
        node = self.node
        class_name = node.name.CamelCase()
        Out = "Out" if node.output else ""
        const = "const" if not node.output else ""

        if node.chained:
            (
                self.out
                << f"PYSUBCLASS_BEGIN(m, pywgpu::{class_name}, ChainedStruct{Out}, {class_name}) {class_name}"
                << "\n"
            )
        else:
            (
                self.out
                << f"PYCLASS_BEGIN(m, pywgpu::{class_name}, {class_name}) {class_name}"
                << "\n"
            )
        self.out.indent()

        for member in node.members:
            if self.exclude_member(member):
                continue

            member_name = member.name.snake_case()
            member_cpp_name = member.name.camelCase()
            member_type = member.type
            member_annotation = member.annotation

            if member_annotation == "const*const*":
                logger.debug(f"Skipping const*const* member {member_name}")
                continue

            # logger.debug(f"member_type: {member_type}")
            if isinstance(member_type, FunctionPointerType):
                logger.debug(f"Skipping function pointer member {member_name}")
                continue

            readonly = (node.extensible is not None and node.extensible == "out") or (
                node.chained is not None and node.chained == "out"
            )
            # def_kind = "def_readonly" if node.extensible and node.extensible == "out" or node.chained and node.chained == "out" else "def_readwrite"
            def_kind = "def_readonly" if readonly else "def_readwrite"
            decoration = self.decorate_member(
                "", self.as_cppType(member_type.name), member
            )
            # print(decoration)

            if decoration == "char const * " and not readonly:
                # print(decoration, readonly)
                self.out << f'.def_property("{member_name}",' << "\n"
                self.out.indent()
                self.out << f"[](const pywgpu::{class_name}& self) {{" << "\n"
                self.out.indent()
                self.out << f"return self.{member_cpp_name};" << "\n"
                self.out.dedent()
                self.out << "}," << "\n"
                (
                    self.out
                    << f"[](pywgpu::{class_name}& self, {decoration} source) {{"
                    << "\n"
                )
                self.out.indent()
                self.out << f"self.{member_cpp_name} = strdup(source);" << "\n"
                self.out.dedent()
                self.out << "}" << "\n"
                self.out.dedent()
                self.out << ")" << "\n"
            else:
                (
                    self.out
                    << f'.{def_kind}("{member_name}", &pywgpu::{class_name}::{member_cpp_name})'
                    << "\n"
                )

        if node.name.get() == "surface texture":
            logger.debug(
                f"surface texture node: {node}"
            )
        if node.output:
        #if node.extensible == "out":
            self.render_init()
        else:
            self.render_kw_init()

        self.out.dedent()
        self.out << ";\n"
        self.out << f"PYCLASS_END(m, pywgpu::{class_name}, {class_name})" << "\n\n"

    def render_init(self):
        self.out << f".def(py::init<>())" << "\n"


    def render_kw_init(self):
        node = self.node

        class_name = node.name.CamelCase()

        self.out << f".def(py::init([](const py::kwargs& kwargs) {{" << "\n"
        self.out.indent()
        self.out << f"pywgpu::{class_name} obj{{}};" << "\n"

        members_by_name = {member.name: member for member in node.members}
        excluded_names = {
            Name.intern(member.length)
            for member in node.members
            if member.length and isinstance(member.length, str)
        }

        members = [
            member
            for member in node.members
            if member.name not in excluded_names
        ]

        allowed_names = [ member.name for member in members ]
        '''
        required_names = [
            member.name
            for member in members
            if not member.optional and not member.default_value
        ]
        '''
        required_names = []

        for member in members:
            if member.optional:
                continue
            if member.default_value is not None:
                continue

            # ???
            member_type = member.type

            if isinstance(member_type, EnumType) or isinstance(member_type, BitmaskType):
                # logger.debug(f"Skipping enum member {member.name}")
                continue

            if isinstance(member_type, StructureType) and not member.annotation:
                continue

            '''
            if isinstance(member_type, StructureType) and member_type.extensible is False:
                continue
            '''

            length_member = members_by_name.get(
                Name.intern(member.length)
            ) if member.length and isinstance(member.length, str) else None

            if length_member is not None:
                if length_member.default_value is not None:
                    logger.debug(
                        f"Skipping member {member.name}, length: {length_member.name} with default value"
                    )
                    continue

            required_names.append(member.name)

        def cpp_string_list(names):
            return "{" + ", ".join(f'"{name.snake_case()}"' for name in names) + "}"
        
        self.out << f'static const std::set<std::string> allowed = {cpp_string_list(allowed_names)};' << "\n"
        self.out << f'static const std::set<std::string> required = {cpp_string_list(required_names)};' << "\n"

        self.out << '''
        // Check for unknown keys
        for (auto& item : kwargs) {
            std::string key = py::cast<std::string>(item.first);
            if (!allowed.count(key)) {
                throw py::key_error("Unknown keyword argument: '" + key + "'");
            }
        }

        // Check for required keys
        for (const auto& key : required) {
            if (!kwargs.contains(key.c_str())) {
                throw py::key_error("Missing required keyword argument: '" + key + "'");
            }
        }
        \n'''

        for member in members:
            if member.name in excluded_names:
                continue
            if self.exclude_member(member):
                continue

            member_name = member.name.snake_case()
            member_cpp_name = member.name.camelCase()
            member_type = member.type
            member_annotation = member.annotation

            if member_annotation == "const*const*":
                logger.debug(f"Skipping const*const* member {member_name}")
                continue

            # logger.debug(f"member_type: {member_type}")
            if isinstance(member_type, FunctionPointerType):
                logger.debug(f"Skipping function pointer member {member_name}")
                continue

            self.out << f'if (kwargs.contains("{member_name}"))' << "\n"
            self.out << "{" << "\n"
            self.out.indent()

            cppType = self.as_annotated_cppType(member, node.has_free_members_function)

            stripped_cppType = cppType.replace("const ", "").replace(" *", "")

            if member.length:
                length_member = None
                if isinstance(member.length, str):
                    length_member = members_by_name.get(Name.intern(member.length))
                    if length_member is not None:
                        length_member_cpp_name = length_member.name.camelCase()

                stripped_cppType = cppType.replace("const ", "").replace(" *", "")
                # print(f"stripped_cppType: {stripped_cppType}")
                if stripped_cppType == "char":
                    (
                        self.out
                        << f'auto value = kwargs["{member_name}"].cast<std::string>();'
                        << "\n"
                    )
                    (
                        self.out
                        << f"obj.{member_cpp_name} = strdup(value.c_str());"
                        << "\n"
                    )
                    if length_member is not None:
                        (
                            self.out
                            << f"obj.{length_member_cpp_name} = value.size();"
                            << "\n"
                        )
                else:
                    (
                        self.out
                        << f'auto _value = kwargs["{member_name}"].cast<std::vector<{stripped_cppType}>>();'
                        << "\n"
                    )
                    self.out << f"auto count = _value.size();" << "\n"
                    self.out << f"auto value = new {stripped_cppType}[count];" << "\n"
                    (
                        self.out
                        << f"std::copy(_value.begin(), _value.end(), value);"
                        << "\n"
                    )
                    self.out << f"obj.{member_cpp_name} = value;" << "\n"
                    if length_member is not None:
                        self.out << f"obj.{length_member_cpp_name} = count;" << "\n"
            else:
                (
                    self.out
                    << f'auto value = kwargs["{member_name}"].cast<{cppType}>();'
                    #<< f'auto value = kwargs["{member_name}"].cast<{stripped_cppType}>();'
                    << "\n"
                )
                self.out << f"obj.{member_cpp_name} = value;" << "\n"

            self.out.dedent()
            self.out << "}" << "\n"
        self.out << "return obj;" << "\n"
        self.out.dedent()
        self.out << "}), py::return_value_policy::automatic_reference)" << "\n"
