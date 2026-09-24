from ...node import FunctionalNode
from ...pyname_registry import PyKind

from ..py_signature import PySignature
from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("function")
@PyiRendererRegistry.register("function_template_specialization")
@PyiRendererRegistry.register("method")
@PyiRendererRegistry.register("ctor")
class PyiFunctionalRenderer(PyiNodeRenderer[FunctionalNode]):
    def render(self):
        node = self.node
        pysig = PySignature.from_node(node, self.format_field)

        is_ctor = node.kind == "ctor"
        is_method = node.kind in ("method", "ctor") or node.mogrified
        is_static = self.is_static()

        if self.is_overloaded():
            self.context.add_import("typing", "overload")
            self.out("@overload")
        if is_static:
            self.out("@staticmethod")

        params = ["self"] if is_method and not is_static else []
        for p in pysig.params:
            default = " = ..." if p.has_default else ""
            params.append(f"{p.name}: {self.types.map(p.param.type)}{default}")

        name = "__init__" if is_ctor else node.pyname
        returns = "None" if is_ctor else self.return_annotation(pysig)
        self.out(f"def {name}({', '.join(params)}) -> {returns}: ...")

    def is_static(self) -> bool:
        node = self.node
        if node.binding is not None:
            return node.binding.kind is PyKind.STATIC_METHOD
        return node.kind == "method" and node.cursor.is_static_method()

    def is_overloaded(self) -> bool:
        node = self.node
        if node.mogrified or node.parent is None:
            return False
        name = node.pyname
        siblings = [
            c for c in node.parent.children
            if isinstance(c, FunctionalNode)
            and c.kind == node.kind
            and (c.kind == "ctor" or c.pyname == name)
        ]
        return len(siblings) > 1

    def return_annotation(self, pysig: PySignature) -> str:
        parts = []
        if pysig.returns_value:
            parts.append(self.types.map(self.node.returns.type))
        parts += [self.types.map(p.type) for p in pysig.out_params]

        if not parts:
            return "None"
        if len(parts) == 1:
            return parts[0]
        return f"tuple[{', '.join(parts)}]"
