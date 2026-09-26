from ...node import StructuralNode, CtorNode
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
                else:
                    self.context.render_node(child)

            # Real members and synthesized extras (inits, __repr__, used
            # functions, properties) are all children.
            self.render_children(node.children, render_one)
            self.render_stub_members()

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

    def render_stub_members(self):
        spec = self.node.spec
        if spec is None:
            return
        for dotted in spec.stub.imports:
            module, _, name = dotted.rpartition(".")
            self.context.add_import(module, name) if module else self.context.add_import(name)
        for line in spec.stub.members:
            self.out(line)

    def has_init(self) -> bool:
        """Whether a constructor is bound: real, synthesized, or declared by hand."""
        if any(isinstance(c, (CtorNode, InitNode)) for c in self.node.children):
            return True
        spec = self.node.spec
        return spec is not None and any("def __init__" in l for l in spec.stub.members)