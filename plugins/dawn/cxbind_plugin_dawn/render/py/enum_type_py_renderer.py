from ..enum_type_renderer import EnumTypeRenderer


class EnumTypePyRenderer(EnumTypeRenderer):
    def render(self):
        enum_name = self.node.name.CamelCase()

        self.out << f"py::enum_<{enum_name}>(m, \"{enum_name}\", py::arithmetic())" << "\n"
        #self.out << f"py::enum_<{enum_name}>(m, \"{enum_name}\")" << "\n"

        with self.out:
            for value in self.node.values:
                value_name = self.as_cppEnum(value.name)
                py_value_name = self.as_pyEnum(value.name)
                self.out << f".value(\"{py_value_name}\", {enum_name}::{value_name})" << "\n"

        self.out << ";\n\n"