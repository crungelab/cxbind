from typing import (
    TypeVar,
    Generic,
    Any,
    Generator,
)

from loguru import logger

from cxbind.extra import ExtraMethod, ExtraInitMethod, ExtraReprMethod, ExtraProperty

from ...node import StructuralNode, FunctionalNode, FieldNode

from .node_renderer import NodeRenderer

T_Node = TypeVar("T_Node", bound=StructuralNode)

class StructuralRenderer(NodeRenderer[T_Node], Generic[T_Node]):
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
        # logger.debug(f"spec: {spec}")
        for method in spec.extra.methods:
            # logger.debug(f"rendering extra method: {method.name} for node: {node.name}")
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

    def render_using(self, method: ExtraMethod):
        use_node: FunctionalNode = self.session.node_registry.get(method.use)
        if use_node is not None:
            other_node = use_node.clone()
            other_node.mogrified = True
            other_node.pyname = method.name
            self.context.render_node(other_node)

    def render_init(self, method: ExtraInitMethod):
        self.begin_chain()
        if method.use is not None:
            self.out(
                f".def(py::init(&{method.use.name}))"
            )
        else:
            self.out(f".def(py::init<>())")

    def render_args_init(self, method: ExtraInitMethod):
        logger.debug("renderering args_init for: {self.node}")
        self.begin_chain()
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
        node = self.node
        self.out(f".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            if method.use is not None:
                self.out(f"{node.name} obj = {method.use.name}();")
            elif node.spec.identity is not None:
                self.out(f"{node.name} obj = {node.spec.identity};")
            else:
                self.out(f"{node.name} obj{{}};")

            allowed_pynames = self.collect_allowed_pynames(node)
            self.render_kwargs_validation(allowed_pynames)

            for child in node.children:
                if type(child) is FieldNode:
                    if child.spec.flatten:
                        logger.debug(f"Flattening field: {child.first_name}")
                        self.render_kwarg_field_flattened(child)
                    else:
                        self.render_kwarg_field(
                            target=f"obj.{child.first_name}",
                            pyname=child.pyname,
                            cursor=child.cursor,
                        )
            self.out("return obj;")
        self.out("}))")

    def collect_allowed_pynames(self, node) -> list[str]:
        """Gather every kwarg name this init will accept, including flattened nested fields."""
        names = []
        for child in node.children:
            if type(child) is FieldNode:
                if child.spec.flatten:
                    record_type = child.cursor.type.get_canonical()
                    for nested_cursor in record_type.get_fields():
                        names.append(self.format_field(nested_cursor.spelling))
                else:
                    names.append(child.pyname)
        return names

    def render_kwargs_validation(self, allowed_pynames: list[str]):
        """Emit a check that throws py::value_error if any kwarg key isn't in the allowed set."""
        set_items = ", ".join(f'"{name}"' for name in allowed_pynames)
        self.out(f"static const std::unordered_set<std::string> allowed_keys = {{{set_items}}};")
        self.out("for (auto item : kwargs)")
        self.out("{")
        with self.out:
            self.out('std::string key = py::str(item.first);')
            self.out("if (allowed_keys.find(key) == allowed_keys.end())")
            self.out("{")
            with self.out:
                self.out(
                    'throw py::value_error("Unexpected keyword argument: \'" + key + "\'");'
                )
            self.out("}")
        self.out("}")

    '''
    def render_kwargs_init(self, method: ExtraInitMethod):
        logger.debug("renderering kwargs_init for: {self.node}")
        self.begin_chain()
        node = self.node
        self.out(f".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            if method.use is not None:
                self.out(f"{node.name} obj = {method.use.name}();")
            else:
                self.out(f"{node.name} obj{{}};")
            for child in node.children:
                if type(child) is FieldNode:
                    if child.spec.flatten:
                        logger.debug(f"Flattening field: {child.first_name}")
                        self.render_kwarg_field_flattened(child)
                    else:
                        self.render_kwarg_field(
                            target=f"obj.{child.first_name}",
                            pyname=child.pyname,
                            cursor=child.cursor,
                        )
            self.out("return obj;")
        self.out("}))")
    '''

    def render_kwarg_field(self, target: str, pyname: str, cursor):
        """Emit `if (kwargs.contains(...)) { ... obj.<target> = value; }` for a single field."""
        is_char_ptr = self.is_char_ptr(cursor)
        typename = "std::string" if is_char_ptr else cursor.type.get_canonical().spelling

        self.out(f'if (kwargs.contains("{pyname}"))')
        self.out("{")
        with self.out:
            if is_char_ptr:
                self.out(f'auto _value = kwargs["{pyname}"].cast<{typename}>();')
                self.out(f"char* value = (char*)malloc(_value.size());")
                self.out(f"strcpy(value, _value.c_str());")
            else:
                self.out(f'auto value = kwargs["{pyname}"].cast<{typename}>();')
            self.out(f"{target} = value;")
        self.out("}")

    def render_kwarg_field_flattened(self, child):
        """
        child is a FieldNode whose underlying type is itself a struct (e.g. `b2JointDef base`)
        marked with flatten=True. Walk its fields and emit kwargs handling for each one,
        writing into obj.<child.first_name>.<nested_field>, but keyed on the nested field's
        own pyname (so callers see them as flat kwargs, not nested under "base").
        """
        base_target = f"obj.{child.first_name}"
        record_type = child.cursor.type.get_canonical()

        for nested_cursor in record_type.get_fields():
            nested_pyname = self.format_field(nested_cursor.spelling)
            self.render_kwarg_field(
                target=f"{base_target}.{nested_cursor.spelling}",
                pyname=nested_pyname,
                cursor=nested_cursor,
            )

    '''
    def render_kwargs_init(self, method: ExtraInitMethod):
        logger.debug("renderering kwargs_init for: {self.node}")
        self.begin_chain()
        node = self.node
        self.out(f".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            if method.use is not None:
                self.out(f"{node.name} obj = {method.use.name}();")
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
                    if child.spec.flatten:
                        logger.debug(f"Flattening field: {child.first_name}")
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
        self.out("}))")
    '''

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
                if field.type.base_name == "py::function":
                    self.out(
                        f'ss << "{field.first_name}=" << py::repr(self.{field.first_name}).cast<std::string>();'
                    )
                else:
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
            # use_node = self.session.node_registry.get(method.use)
            use_node = self.runner.node_registry.get(method.use)
            if use_node is not None:
                other_node = use_node.clone()
                other_node.mogrified = True
                other_node.pyname = method.name
                self.context.render_node(other_node)
            else:
                raise ValueError(f"Node not found for method use: {method.use}")
        else:
            logger.warning(
                f"Unsupported extra method '{method.name}' for node {node.name}: no function provided"
            )

    """
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
    """

    def render_extra_properties(self):
        node = self.node
        for prop in node.spec.extra.properties:
            getter = prop.getter
            setter = prop.setter
            self.begin_chain()
            if setter is not None:
                self.out(
                    # f'.def_property("{prop.name}", &{node.name}::{getter}, &{node.name}::{setter})'
                    f'.def_property("{prop.name}", &{getter}, &{setter})'
                )
            else:
                self.out(
                    # f'.def_property_readonly("{prop.name}", &{node.name}::{getter})'
                    f'.def_property_readonly("{prop.name}", &{getter})'
                )
