from loguru import logger

from ...node import StructuralNode, FieldNode
from ...extra_node import (
    InitNode,
    DefaultInitNode,
    FactoryInitNode,
    ArgsInitNode,
    KwargsInitNode,
)

from ..renderer_registry import PbRendererRegistry
from .node_renderer import NodeRenderer


class InitRenderer[T_Node: InitNode](NodeRenderer[T_Node]):
    """Base for synthesized __init__ variants. The structure is the parent."""

    @property
    def structure(self) -> StructuralNode:
        return self.node.parent


@PbRendererRegistry.register("default_init")
class DefaultInitRenderer(InitRenderer[DefaultInitNode]):
    def render(self):
        self.begin_chain()
        self.out(".def(py::init<>())")


@PbRendererRegistry.register("factory_init")
class FactoryInitRenderer(InitRenderer[FactoryInitNode]):
    def render(self):
        self.begin_chain()
        self.out(f".def(py::init(&{self.node.use.name}))")


@PbRendererRegistry.register("args_init")
class ArgsInitRenderer(InitRenderer[ArgsInitNode]):
    def render(self):
        structure = self.structure
        logger.debug(f"rendering args_init for: {structure.name}")
        self.begin_chain()

        args = []
        values = []
        for field in self.node.fields:
            cursor = field.cursor
            if self.is_char_ptr(cursor):
                typename = "std::string"
            else:
                typename = cursor.type.get_canonical().spelling
            arg_name = field.first_name
            args.append(f"{typename} {arg_name}")
            values.append(arg_name)

        self.out(f".def(py::init([]({', '.join(args)})")
        self.out("{")
        with self.out:
            self.out(f"{structure.name} obj{{}};")
            for value in values:
                self.out(f"obj.{value} = {value};")
            self.out("return obj;")
        self.out("}))")


@PbRendererRegistry.register("kwargs_init")
class KwargsInitRenderer(InitRenderer[KwargsInitNode]):
    def render(self):
        structure = self.structure
        node = self.node
        logger.debug(f"rendering kwargs_init for: {structure.name}")
        self.begin_chain()

        self.out(".def(py::init([](const py::kwargs& kwargs)")
        self.out("{")
        with self.out:
            if node.use is not None:
                self.out(f"{structure.name} obj = {node.use.name}();")
            elif node.identity is not None:
                self.out(f"{structure.name} obj = {node.identity};")
            else:
                self.out(f"{structure.name} obj{{}};")

            self.render_kwargs_validation(self.collect_allowed_pynames())

            for field in node.fields:
                if field.spec.flatten:
                    logger.debug(f"Flattening field: {field.first_name}")
                    self.render_kwarg_field_flattened(field)
                else:
                    self.render_kwarg_field(
                        target=f"obj.{field.first_name}",
                        pyname=field.pyname,
                        cursor=field.cursor,
                    )
            self.out("return obj;")
        self.out("}))")

    def collect_allowed_pynames(self) -> list[str]:
        """Every kwarg name this init accepts, including flattened nested fields."""
        names = []
        for field in self.node.fields:
            if field.spec.flatten:
                record_type = field.cursor.type.get_canonical()
                for nested_cursor in record_type.get_fields():
                    names.append(self.format_field(nested_cursor.spelling))
            else:
                names.append(field.pyname)
        return names

    def render_kwargs_validation(self, allowed_pynames: list[str]):
        """Throw py::value_error if any kwarg key isn't in the allowed set."""
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

    def render_kwarg_field(self, target: str, pyname: str, cursor):
        """`if (kwargs.contains(...)) { ... <target> = value; }` for one field."""
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

    def render_kwarg_field_flattened(self, field: FieldNode):
        """
        A field whose type is itself a struct (e.g. `b2JointDef base`) marked
        flatten=True: its nested fields become flat kwargs, written into
        obj.<field>.<nested>, keyed on the nested field's own pyname.
        """
        base_target = f"obj.{field.first_name}"
        record_type = field.cursor.type.get_canonical()

        for nested_cursor in record_type.get_fields():
            self.render_kwarg_field(
                target=f"{base_target}.{nested_cursor.spelling}",
                pyname=self.format_field(nested_cursor.spelling),
                cursor=nested_cursor,
            )
