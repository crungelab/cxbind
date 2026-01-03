from loguru import logger

from ...name import Name
from ...node import FunctionPointerType, StructureType, EnumType, BitmaskType
from ..structure_type_renderer import StructureTypeRenderer

default_map = {
    "nullptr": "None",
    "true": "True",
    "false": "False",
    "zero": 0,
    "copy stride undefined": 0xFFFFFFFF,
    "limit u32 undefined": 0xFFFFFFFF,
    "limit u64 undefined": 0xFFFFFFFFFFFFFFFF,
    "depth slice undefined": 0xFFFFFFFF,
    "mip level count undefined": 0xFFFFFFFF,
    "array layer count undefined": 0xFFFFFFFF,
    #"depth clear value undefined": float('nan'),
    "depth clear value undefined": None, #TODO: handle float('nan') properly
    "query set index undefined": 0xFFFFFFFF,
    "whole size": 0xFFFFFFFFFFFFFFFF,
}

class StructureTypePyRenderer(StructureTypeRenderer):
    def render(self):
        node = self.node
        class_name = node.name.CamelCase()
        Out = "Out" if node.output else ""
        if Out:
            return
        const = "const" if not node.output else ""

        '''
        if node.chained:
            (
                self.out
                << f'py::class_<{class_name}, ChainedStruct{Out}> _{class_name}(m, "{class_name}");'
                << "\n"
            )
        else:
            (
                self.out
                << f'py::class_<{class_name}> _{class_name}(m, "{class_name}");'
                << "\n"
            )
        '''

        self.out / "@dataclass(frozen=True, kw_only=True)" << "\n"
        self.out / f"class {class_name}:" << "\n"
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
            extra = ""
            if member.optional:
                extra = "Optional[Any] = None"
            else:
                extra = "Any"

            member_default = member.default_value
            if member_default is not None:
                if isinstance(member_default, str) and member_default[0].isdigit() and member_default[-1] == 'f':
                    member_default = member_default[:-1]
                if member_default in default_map:
                    member_default = default_map[member_default]
                
                #elif isinstance(member_type, StructureType):
                #    logger.debug(f"Structure member default: {member_default}")
                #    member_default = f"{member_type.name.CamelCase()}()"
                elif isinstance(member_type, EnumType):
                    logger.debug(f"Enum member default: {member_default}")
                    #member_default = f"{member_type.name.CamelCase()}.{Name(member_default).CamelCase()}"
                    member_default = f"{member_type.name.CamelCase()}.{self.as_pyEnum(Name(member_default))}"
                elif isinstance(member_type, BitmaskType):
                    logger.debug(f"Bitmask member default: {member_default}")
                    #member_default = f"{member_type.name.CamelCase()}.{Name(member_default).CamelCase()}"
                    member_default = f"{member_type.name.CamelCase()}.{self.as_pyEnum(Name(member_default))}"
                extra += f" = {member_default}"
            (
                self.out
                #/ f'.{def_kind}("{member_name}", &pywgpu::{class_name}::{member_cpp_name})'
                # / f'{member_name}: Any  # type: {decoration}, default: {member.default_value}'
                / f'{member_name}: {extra}  # type: {decoration}, default: {member_default}'
                << "\n"
            )

        if node.name.get() == "surface texture":
            logger.debug(f"surface texture node: {node}")

        '''
        if node.output:
            # if node.extensible == "out":
            self.render_init()
        else:
            self.render_kw_init()
        '''

        self.out.dedent()
        self.out << "\n\n"

    def render_init(self):
        self.out / f".def(py::init<>())" << "\n"

    def render_kw_init(self):
        node = self.node

        class_name = node.name.CamelCase()

        self.out / f".def(py::init([](const py::kwargs& kwargs) {{" << "\n"
        self.out.indent()
        self.out / f"pywgpu::{class_name} obj{{}};" << "\n"

        members_by_name = {member.name: member for member in node.members}

        excluded_names = {
            member.length_member.name
            for member in node.members
            if member.length_member is not None
        }

        members = [
            member for member in node.members if member.name not in excluded_names
        ]

        allowed_names = [member.name for member in members]
        required_names = []

        for member in members:
            if member.optional:
                continue
            if member.default_value is not None:
                continue

            member_type = member.type

            if isinstance(member_type, EnumType) or isinstance(
                member_type, BitmaskType
            ):
                # logger.debug(f"Skipping enum member {member.name}")
                continue

            if isinstance(member_type, StructureType) and not member.annotation:
                continue

            """
            if isinstance(member_type, StructureType) and member_type.extensible is False:
                continue
            """

            if (
                member.length_member is not None
                and member.length_member.default_value is not None
            ):
                logger.debug(
                    f"Skipping member {member.name}, length: {member.length_member.name} with default value"
                )
                continue

            required_names.append(member.name)

        def cpp_string_list(names):
            return "{" + ", ".join(f'"{name.snake_case()}"' for name in names) + "}"

        (
            self.out
            / f"static const std::set<std::string> allowed = {cpp_string_list(allowed_names)};"
            << "\n"
        )
        (
            self.out
            / f"static const std::set<std::string> required = {cpp_string_list(required_names)};"
            << "\n"
        )

        self.out / """
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
        \n"""

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

            self.out / f'if (kwargs.contains("{member_name}"))' << "\n"
            self.out / "{" << "\n"
            self.out.indent()

            cppType = self.as_annotated_cppType(member, node.has_free_members_function)

            stripped_cppType = cppType.replace("const ", "").replace(" *", "")

            if member.length:
                length_member = member.length_member
                if length_member is not None:
                    length_member_cpp_name = length_member.name.camelCase()

                stripped_cppType = cppType.replace("const ", "").replace(" *", "")
                # print(f"stripped_cppType: {stripped_cppType}")
                if stripped_cppType == "char":
                    (
                        self.out
                        / f'auto value = kwargs["{member_name}"].cast<std::string>();'
                        << "\n"
                    )
                    (
                        self.out / f"obj.{member_cpp_name} = strdup(value.c_str());"
                        << "\n"
                    )
                    if length_member is not None:
                        (
                            self.out / f"obj.{length_member_cpp_name} = value.size();"
                            << "\n"
                        )
                else:
                    (
                        self.out
                        / f'auto _value = kwargs["{member_name}"].cast<std::vector<{stripped_cppType}>>();'
                        << "\n"
                    )
                    self.out / f"auto count = _value.size();" << "\n"
                    self.out / f"auto value = new {stripped_cppType}[count];" << "\n"
                    (
                        self.out / f"std::copy(_value.begin(), _value.end(), value);"
                        << "\n"
                    )
                    self.out / f"obj.{member_cpp_name} = value;" << "\n"
                    if length_member is not None:
                        self.out / f"obj.{length_member_cpp_name} = count;" << "\n"
            else:
                (
                    self.out
                    / f'auto value = kwargs["{member_name}"].cast<{cppType}>();'
                    << "\n"
                )
                self.out / f"obj.{member_cpp_name} = value;" << "\n"

            self.out.dedent()
            self.out / "}" << "\n"
        self.out / "return obj;" << "\n"
        self.out.dedent()
        self.out / "}), py::return_value_policy::automatic_reference)" << "\n"
