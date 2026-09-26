from ...node import StructuralNode, FieldNode, CtorNode
from ...extra_node import InitNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("struct")
@PyiRendererRegistry.register("class")
@PyiRendererRegistry.register("class_template_specialization")
class PyiStructuralRenderer(PyiNodeRenderer[StructuralNode]):
    def render(self):
        node = self.node
        nested: list[StructuralNode] = []

        self.out(f"class {node.pyname}{self.class_args()}:")
        with self.out:
            start = len(self.out.text)
            self.context.push_exports()

            def render_one(child):
                # pybind registers every class at module scope, so nested
                # types go after this class, not inside it.
                if isinstance(child, StructuralNode):
                    nested.append(child)
                elif type(child) is FieldNode and self.is_flattened(child):
                    self.render_flattened_fields(child)
                else:
                    self.context.render_node(child)

            # Real members and synthesized extras (inits, __repr__, used
            # functions) are all children now.
            self.render_children(node.children, render_one)

            self.render_extra_properties()

            if not self.has_init():
                # pybind11's inherited default; always raises TypeError.
                self.context.add_import("typing", "Any")
                self.out("def __init__(self, *args: Any, **kwargs: Any) -> None: ...")

            # Constants that nested enums exported into this class.
            for name, type_path in self.context.pop_exports().items():
                self.out(f"{name}: ClassVar[{type_path}]")

            if len(self.out.text) == start:
                self.out("...")
        self.out()

        for child in nested:
            self.context.render_node(child)

    def class_args(self) -> str:
        """Everything inside `class Name(...)`: base classes plus the metaclass."""
        spec = self.node.spec
        args = []
        if spec is not None and spec.extends:
            args += [self.types.class_name(b) or self.types.any(b) for b in spec.extends]
        # pybind11 creates every class with its own metaclass; stubtest
        # requires the stub to declare one too.
        args.append("metaclass=_pybind11_type")
        return f"({', '.join(args)})"

    def has_init(self) -> bool:
        """Whether pb binds a constructor: real or synthesized."""
        return any(isinstance(c, (CtorNode, InitNode)) for c in self.node.children)

    # --- fields ----------------------------------------------------------

    @staticmethod
    def is_flattened(field: FieldNode) -> bool:
        return field.spec is not None and field.spec.flatten

    def render_flattened_fields(self, field: FieldNode):
        record = field.cursor.type.get_canonical()
        for nested in record.get_fields():
            self.out(f"{self.format_field(nested.spelling)}: {self.types.map_cx(nested.type)}")

    # --- extras still driven by the spec ---------------------------------

    def render_extra_properties(self):
        for prop in self.node.extra.properties:
            self.context.add_import("typing", "Any")
            self.out("@property")
            self.out(f"def {prop.name}(self) -> Any: ...")
            if prop.setter is not None:
                self.out(f"@{prop.name}.setter")
                self.out(f"def {prop.name}(self, value: Any) -> None: ...")
