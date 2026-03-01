from loguru import logger

from cxbind.extra import ExtraMethod, ExtraInitMethod, ExtraReprMethod, ExtraProperty

from ...node import StructBaseNode, FieldNode

from .node_renderer import NodeRenderer, T_Node
from .method_renderer import MethodRenderer

class StructBaseRenderer(NodeRenderer[T_Node]):
    def render(self):
        node = self.node
        pyname = node.pyname

        self.end_chain()

        extra = f", {', '.join(node.spec.extends)}" if node.spec.extends else ""

        extra += f",{node.spec.holder}<{node.name}>" if node.spec.holder else ""

        self.out(
            f'py::class_<{node.name}{extra}> _{pyname}(_{self.module}, "{pyname}");'
        )
        self.out(f'registry.on(_{self.module}, "{pyname}", _{pyname});')

        with self.enter(node):
            super().render()

            self.render_extra_methods()

            self.render_extra_properties()

        self.end_chain()

    def render_extra_methods(self):
        node = self.node
        spec = node.spec
        #logger.debug(f"spec: {spec}")
        for method in spec.extra.methods:
            logger.debug(f"rendering extra method: {method.name} for node: {node.name}")
            if method.name == "__init__":
                if method.gen_kwargs:
                    self.render_kwargs_init(method)
                elif method.gen_args:
                    self.render_args_init(method)
                else:
                    self.render_init(method)
            elif method.name == "__repr__":
                self.render_repr(method)
            else:
                self.render_standard_method(method)


    def render_init(self, method: ExtraInitMethod):
        self.begin_chain()
        if method.use is not None:
            self.out(
                #f'.def("{method.name}", &{method.use})'
                #.def(py::init([](const py::kwargs& kwargs)
                f'.def(py::init(&{method.use}))'
            )
        else:
            self.out(f".def(py::init<>())")

    """
    def render_init(self, method: ExtraInitMethod):
        self.begin_chain()
        self.out(f".def(py::init<>())")
    """

    def render_args_init(self, method: ExtraInitMethod):
        logger.debug("renderering args_init for: {self.node}")
        self.begin_chain()
        # node = self.top_node
        node = self.node
        args = []
        values = []
        for child in node.children:
            if not isinstance(child, FieldNode):
                continue
            cursor = child.cursor
            typename = None
            is_char_ptr = self.is_char_ptr(cursor)
            if is_char_ptr:
                typename = "std::string"
            else:
                # typename = cursor.type.spelling
                typename = cursor.type.get_canonical().spelling

            # arg_name = child.name.split("::")[-1]
            arg_name = child.first_name
            args.append(f"{typename} {arg_name}")
            values.append(f"{arg_name}")

        self.out(f".def(py::init([]({', '.join(args)})")
        self.out("{")
        with self.out:
            self.out(f"{node.name} obj{{}};")
            for value in values:
                self.out(f"obj.{value} = {value};")
            self.out("return obj;")
        # self.out("}), py::return_value_policy::automatic_reference);")
        # self.out("}));")
        self.out("}))")

    def render_kwargs_init(self, method: ExtraInitMethod):
        logger.debug("renderering kwargs_init for: {self.node}")
        self.begin_chain()
        # node = self.top_node
        node = self.node
        self.out(f".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            if method.use is not None:
                self.out(f"{node.name} obj = {method.use}();")
            else:
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
                        self.out(f"obj.{child.first_name} = value;")
                    self.out("}")
            self.out("return obj;")
        # self.out("}), py::return_value_policy::automatic_reference);")
        # self.out("}));")
        self.out("}))")

    def render_repr(self, method: ExtraReprMethod):
        node = self.node
        spec = node.spec
        logger.debug(f"rendering __repr__ for: {node.name}")
        self.begin_chain()

        # 1. Determine which members to include
        fields_to_render = []

        if method.auto == True:
            # Automatically grab all FieldNodes (public members)
            fields_to_render = [c for c in node.children if isinstance(c, FieldNode)]
        else:
            # Manual opt-in: Filter children by the names provided in the spec
            for m_name in spec.members:
                child = next(
                    (
                        c
                        for c in node.children
                        if isinstance(c, FieldNode) and c.first_name == m_name
                    ),
                    None,
                )
                if child:
                    fields_to_render.append(child)
                else:
                    logger.warning(f"Field {m_name} not found in {node.name}")

        # 2. Generate the pybind11 binding code
        self.out(f'.def("__repr__", [](const {node.name} &self) {{')
        with self.out:
            self.out("std::stringstream ss;")
            # self.out(f'ss << "{node.name}(";')
            self.out(f'ss << "{node.pyname}(";')

            for i, field in enumerate(fields_to_render):
                if i > 0:
                    self.out('ss << ", ";')

                # Use field.first_name for the label and the C++ access
                self.out(
                    f'ss << "{field.first_name}=" << py::repr(py::cast(self.{field.first_name})).cast<std::string>();'
                )

            self.out('ss << ")";')
            self.out("return ss.str();")
        self.out("})")

    def render_standard_method(self, method: ExtraMethod):
        node = self.node
        self.begin_chain()
        if method.use is not None:
            self.out(
                f'.def("{method.name}", &{method.use})'
            )
        else:
            logger.warning(
                f"Unsupported extra method '{method.name}' for node {node.name}: no function provided"
            )

    def render_extra_properties(self):
        node = self.node
        for prop in node.spec.extra.properties:
            getter = prop.getter
            setter = prop.setter
            self.begin_chain()
            if setter is not None:
                self.out(
                    #f'.def_property("{prop.name}", &{node.name}::{getter}, &{node.name}::{setter})'
                    f'.def_property("{prop.name}", &{getter}, &{setter})'
                )
            else:
                self.out(
                    #f'.def_property_readonly("{prop.name}", &{node.name}::{getter})'
                    f'.def_property_readonly("{prop.name}", &{getter})'
                )
