from loguru import logger

from .node_builder import NodeBuilder, T_Node
from ..node import StructBaseNode, FieldNode, TypedefNode
from .. import cu

class StructBaseBuilder(NodeBuilder[T_Node]):
    def create_pyname(self, name):
        pyname = super().create_pyname(name)
        if isinstance(self.top_node, StructBaseNode):
            return f'{self.top_node.pyname}{pyname}'
        return pyname

    def should_cancel(self):
        if not self.is_class_mappable(self.cursor):
            return True
        # Only map top level classes for now
        if isinstance(self.top_node, StructBaseNode):
            return True
        if isinstance(self.top_node, TypedefNode):
            return True
        return super().should_cancel()

    def is_class_mappable(self, cursor):
        if(cursor.spelling == 'Init'):
            return False
        if not self.is_cursor_mappable(cursor):
            return False
        if not cursor.is_definition():
            return False
        return True

    def gen_init(self):
        #self.out(f"{self.scope}.def(py::init<>());")
        self.out(f".def(py::init<>())")

    def gen_kw_init(self):
        node = self.top_node
        #self.out(f'{self.scope}.def(py::init([](const py::kwargs& kwargs)')
        self.out(f'.def(py::init([](const py::kwargs& kwargs)')
        self.out("{")
        with self.out:
            self.out(f'{node.name} obj{{}};')
            for child in node.children:
                cursor = child.cursor
                typename = None
                is_char_ptr = self.is_char_ptr(cursor)
                if is_char_ptr:
                    typename = 'std::string'
                else:
                    #typename = cursor.type.spelling
                    typename = cursor.type.get_canonical().spelling
                if type(child) is FieldNode:
                    self.out(f'if (kwargs.contains("{child.pyname}"))')
                    self.out("{")
                    with self.out:
                        if is_char_ptr:
                            self.out(f'auto _value = kwargs["{child.pyname}"].cast<{typename}>();')
                            self.out(f'char* value = (char*)malloc(_value.size());')
                            self.out(f'strcpy(value, _value.c_str());')
                        else:
                            self.out(f'auto value = kwargs["{child.pyname}"].cast<{typename}>();')
                        self.out(f'obj.{child.name} = value;')
                    self.out("}")
            self.out('return obj;')
        self.out("}), py::return_value_policy::automatic_reference);")
