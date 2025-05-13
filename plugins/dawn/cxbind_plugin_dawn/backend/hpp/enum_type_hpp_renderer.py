from ..enum_type_renderer import EnumTypeRenderer


class EnumTypeHppRenderer(EnumTypeRenderer):
    def render(self):
        enum_name = self.node.name.CamelCase()

        self.out << f"enum class {enum_name} : uint32_t {{" << "\n"

        with self.out:
            for value in self.node.values:
                value_name = value.name.CamelCase()
                suffix = value_name
                if value_name[0].isdigit():
                    value_name = f"e{value_name}"
                self.out << f"{value_name} = WGPU{enum_name}_{suffix}," << "\n"


        self.out << "};\n\n"