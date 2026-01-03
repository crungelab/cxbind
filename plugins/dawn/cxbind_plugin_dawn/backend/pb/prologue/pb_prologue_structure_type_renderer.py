from loguru import logger

from ....name import Name
from ....node import FunctionPointerType, StructureType, EnumType, BitmaskType
from ...structure_type_renderer import StructureTypeRenderer


class PbPrologueStructureTypeRenderer(StructureTypeRenderer):
    def render(self):
        node = self.node
        if node.output:
            return

        class_name = node.name.CamelCase()

        self.out / f"pywgpu::{class_name}* build{class_name}(py::handle handle, LinearAlloc& la) {{" << "\n"
        self.out.indent()
        #self.out / f"pywgpu::{class_name} obj{{}};" << "\n"
        self.out / f"auto& obj = *la.make<pywgpu::{class_name}>();" << "\n"

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

            #self.out / f'if (kwargs.contains("{member_name}"))' << "\n"
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
                        / f'auto py_list = handle.attr("{member_name}").cast<py::sequence>();'
                        << "\n"
                    )
                    self.out / f"uint32_t count = static_cast<uint32_t>(py_list.size());" << "\n"
                    self.out / f"auto* value = la.alloc_array<{stripped_cppType}>(count);" << "\n"
                    self.out / "for (uint32_t i = 0; i < count; ++i) {" << "\n"
                    self.out.indent()
                    self.out / f"value[i] = py_list[i].cast<{stripped_cppType}>();" << "\n"
                    self.out.dedent()
                    self.out / "}" << "\n" << "\n"

                    self.out / f"obj.{member_cpp_name} = value;" << "\n"
                    if length_member is not None:
                        self.out / f"obj.{length_member_cpp_name} = count;" << "\n"
            else:
                (
                    self.out
                    / f'auto value = handle.attr("{member_name}").cast<{cppType}>();'
                    << "\n"
                )
                self.out / f"obj.{member_cpp_name} = value;" << "\n"

            self.out.dedent()
            self.out / "}" << "\n"

        self.out / "return &obj;" << "\n"
        self.out.dedent()
        self.out / "}" << "\n" << "\n"
