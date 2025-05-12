from ..bitmask_type_renderer import BitmaskTypeRenderer


class BitmaskTypeHppRenderer(BitmaskTypeRenderer):
    def render(self):
        enum_name = self.node.name.CamelCase()

        self.out << f"enum class {enum_name} : uint64_t {{" << "\n"

        with self.out:
            for value in self.node.values:
                value_name = value.name.CamelCase()
                suffix = value_name
                if value_name[0].isdigit():
                    value_name = f"e{value_name}"
                self.out << f"{value_name} = WGPU{enum_name}_{suffix}," << "\n"

        self.out << "};\n"

        self.out(f"""
template<>
struct IsWGPUBitmask<pywgpu::{enum_name}> {{
    static constexpr bool enable = true;
}};

""")
