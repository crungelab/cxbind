from .node_builder import NodeBuilder
from ..node import StructOrClass, Field, Typedef


class StructOrClassBuilder(NodeBuilder[StructOrClass]):
    def create_node(self):
        self.node = StructOrClass(self.fqname, self.cursor)

    def create_pyname(self, name):
        pyname = super().create_pyname(name)
        if isinstance(self.top_node, StructOrClass):
            return f'{self.top_node.pyname}{pyname}'
        return pyname

    def should_cancel(self):
        return super().should_cancel() or not self.is_class_mappable(self.cursor) or isinstance(self.top_node, Typedef)

    def gen_init(self):
        self(f"{self.scope}.def(py::init<>());")

    def gen_kw_init(self):
        node = self.top_node
        self(f'{self.scope}.def(py::init([](const py::kwargs& kwargs)')
        self("{")
        with self:
            self(f'{node.fqname} obj;')
            for child in node.children:
                cursor = child.cursor
                typename = None
                is_char_ptr = self.is_char_ptr(cursor)
                if is_char_ptr:
                    typename = 'std::string'
                else:
                    typename = cursor.type.spelling
                if type(child) is Field:
                    self(f'if (kwargs.contains("{child.pyname}"))')
                    self("{")
                    with self:
                        if is_char_ptr:
                            self(f'auto _value = kwargs["{child.pyname}"].cast<{typename}>();')
                            self(f'char* value = (char*)malloc(_value.size());')
                            self(f'strcpy(value, _value.c_str());')
                        else:
                            self(f'auto value = kwargs["{child.pyname}"].cast<{typename}>();')
                        self(f'obj.{child.name} = value;')
                    self("}")
            self('return obj;')
        self("}), py::return_value_policy::automatic_reference);")
