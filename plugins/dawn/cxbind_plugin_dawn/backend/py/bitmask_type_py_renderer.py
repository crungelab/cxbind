from ..bitmask_type_renderer import BitmaskTypeRenderer


class BitmaskTypePyRenderer(BitmaskTypeRenderer):
    def render(self):
        enum_name = self.node.name.CamelCase()

        self.out << f"py::enum_<{enum_name}>(m, \"{enum_name}\", py::arithmetic())" << "\n"

        self.out.indent()

        for value in self.node.values:
            value_name = self.as_cppEnum(value.name)
            py_value_name = self.as_pyEnum(value.name)
            self.out << f".value(\"{py_value_name}\", {enum_name}::{value_name})" << "\n"

        self.out(f"""
        .def("__or__", [](pywgpu::{enum_name}& a, pywgpu::{enum_name}& b) {{
            return (pywgpu::{enum_name})(a | b);
        }}, py::is_operator());
        """)

        self.out.dedent()
        self.out << "\n"