from loguru import logger

from .node_renderer import NodeRenderer, T_Node
from ...node import StructBaseNode, FieldNode


class StructBaseRenderer(NodeRenderer[T_Node]):
    def render(self):
        node = self.node

        self.end_chain()

        extra = f", {', '.join(node.spec.extends)}" if node.spec.extends else ""

        extra += f",{node.spec.holder}<{node.name}>" if node.spec.holder else ""

        self.out(
            f'py::class_<{node.name}{extra}> _{node.pyname}(_{self.module}, "{node.pyname}");'
        )
        self.out(f'registry.on(_{self.module}, "{node.pyname}", _{node.pyname});')

        with self.enter(node):
            super().render()

            if node.spec.gen_init:
                self.render_init()
            elif node.spec.gen_kw_init:
                self.render_kw_init()

            self.render_properties()

        self.end_chain()

    def render_init(self):
        self.begin_chain()
        self.out(f".def(py::init<>())")

    def render_kw_init(self):
        self.begin_chain()
        node = self.top_node
        self.out(f".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            self.out(f"{node.name} obj{{}};")
            for child in node.children:
                cursor = child.cursor
                typename = None
                is_char_ptr = self.is_char_ptr(cursor)
                if is_char_ptr:
                    typename = "std::string"
                else:
                    # typename = cursor.type.spelling
                    typename = cursor.type.get_canonical().spelling
                if type(child) is FieldNode:
                    self.out(f'if (kwargs.contains("{child.pyname}"))')
                    self.out("{")
                    with self.out:
                        if is_char_ptr:
                            self.out(
                                f'auto _value = kwargs["{child.pyname}"].cast<{typename}>();'
                            )
                            self.out(f"char* value = (char*)malloc(_value.size());")
                            self.out(f"strcpy(value, _value.c_str());")
                        else:
                            self.out(
                                f'auto value = kwargs["{child.pyname}"].cast<{typename}>();'
                            )
                        self.out(f"obj.{child.name} = value;")
                    self.out("}")
            self.out("return obj;")
        self.out("}), py::return_value_policy::automatic_reference);")

    def render_properties(self):
        node = self.node
        for prop in node.spec.properties:
            getter = prop.getter
            setter = prop.setter
            self.begin_chain()
            if setter is not None:
                self.out(
                    f'.def_property("{prop.name}", &{node.name}::{getter}, &{node.name}::{setter})'
                )
            else:
                self.out(
                    f'.def_property_readonly("{prop.name}", &{node.name}::{getter})'
                )
