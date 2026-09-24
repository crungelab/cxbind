from cxbind.extra import ExtraMethod, ExtraInitMethod

from ...node import StructuralNode, FunctionalNode, FieldNode
from ...pyname_registry import PyBinding, PyKind

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("struct")
@PyiRendererRegistry.register("class")
@PyiRendererRegistry.register("class_template_specialization")
class PyiStructuralRenderer(PyiNodeRenderer[StructuralNode]):
    def render(self):
        node = self.node
        nested: list[StructuralNode] = []

        self.out(f"class {node.pyname}{self.bases()}:")
        with self.out:
            start = len(self.out.text)

            for child in node.children:
                # pybind registers every class at module scope, so nested
                # types go after this class, not inside it.
                if isinstance(child, StructuralNode):
                    nested.append(child)
                elif type(child) is FieldNode and self.is_flattened(child):
                    self.render_flattened_fields(child)
                else:
                    self.context.render_node(child)

            self.render_extra_methods()
            self.render_extra_properties()

            if len(self.out.text) == start:
                self.out("...")
        self.out()

        for child in nested:
            self.context.render_node(child)

    def bases(self) -> str:
        spec = self.node.spec
        if spec is None or not spec.extends:
            return ""
        names = [self.types.class_name(base) or self.types.any(base) for base in spec.extends]
        return f"({', '.join(names)})"

    # --- fields ----------------------------------------------------------

    @staticmethod
    def is_flattened(field: FieldNode) -> bool:
        return field.spec is not None and field.spec.flatten

    def flattened_fields(self, field: FieldNode) -> list[tuple[str, str]]:
        record = field.cursor.type.get_canonical()
        return [
            (self.format_field(nested.spelling), self.types.map_cx(nested.type))
            for nested in record.get_fields()
        ]

    def render_flattened_fields(self, field: FieldNode):
        for name, annotation in self.flattened_fields(field):
            self.out(f"{name}: {annotation}")

    def init_fields(self) -> list[tuple[str, str]]:
        """(pyname, annotation) for every field an __init__ can set, flattened included."""
        out = []
        for child in self.node.children:
            if type(child) is not FieldNode:
                continue
            if self.is_flattened(child):
                out += self.flattened_fields(child)
            elif child.type is not None:
                out.append((child.pyname, self.types.map(child.type)))
            else:
                out.append((child.pyname, self.types.map_cx(child.cursor.type)))
        return out

    # --- extras ----------------------------------------------------------

    def render_extra_methods(self):
        spec = self.node.spec
        if spec is None:
            return
        for method in spec.extra.methods:
            if method.name == "__init__":
                self.render_init(method)
            elif method.name == "__repr__":
                self.out("def __repr__(self) -> str: ...")
            else:
                self.render_standard_method(method)

    def render_init(self, method: ExtraInitMethod):
        if method.gen_kwargs:
            params = [f"{name}: {ann} = ..." for name, ann in self.init_fields()]
            params = ["self", "*", *params] if params else ["self"]
        elif method.gen_args:
            params = ["self", *(f"{name}: {ann}" for name, ann in self.init_fields())]
        elif method.use is not None:
            # py::init(&factory): the factory's signature, unknown here.
            self.context.add_import("typing", "Any")
            params = ["self", "*args: Any", "**kwargs: Any"]
        else:
            params = ["self"]
        self.out(f"def __init__({', '.join(params)}) -> None: ...")

    def render_standard_method(self, method: ExtraMethod):
        if method.use is None:
            return
        use_node: FunctionalNode = self.runner.node_registry.get(method.use)
        if use_node is None:
            return
        # Same as pb: render the free function as a method under method.name.
        other = use_node.clone()
        other.mogrified = True
        other.binding = PyBinding(
            other, PyKind.METHOD, self.node.binding, method.name, explicit=True
        )
        self.context.render_node(other)

    def render_extra_properties(self):
        spec = self.node.spec
        if spec is None:
            return
        for prop in spec.extra.properties:
            self.context.add_import("typing", "Any")
            self.out("@property")
            self.out(f"def {prop.name}(self) -> Any: ...")
            if prop.setter is not None:
                self.out(f"@{prop.name}.setter")
                self.out(f"def {prop.name}(self, value: Any) -> None: ...")
