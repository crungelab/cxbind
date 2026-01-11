from ..enum_type_renderer import EnumTypeRenderer


class PyiEnumTypeRenderer(EnumTypeRenderer):
    def render(self):
        enum_name = self.node.name.CamelCase()

        self.out << f"class {enum_name}(IntEnum):" << "\n"

        with self.out:
            for value in self.node.values:
                value_name = self.as_cppEnum(value.name)
                py_value_name = self.as_pyEnum(value.name)
                #self.out / f"{py_value_name} = {value.value}" << "\n"
                self.out / f"{py_value_name}: int" << "\n"

        self.out << "\n\n"