from ...node import FieldNode
from ...extra_node import InitNode, ArgsInitNode, KwargsInitNode

from ..renderer_registry import PyiRendererRegistry
from .pyi_node_renderer import PyiNodeRenderer


@PyiRendererRegistry.register("default_init")
@PyiRendererRegistry.register("factory_init")
@PyiRendererRegistry.register("args_init")
@PyiRendererRegistry.register("kwargs_init")
class PyiInitRenderer(PyiNodeRenderer[InitNode]):
    """Every synthesized __init__ is one `def __init__(...)` line."""

    def render(self):
        self.out(f"def __init__({', '.join(self.params())}) -> None: ...")

    def params(self) -> list[str]:
        node = self.node
        match node.kind:
            case "kwargs_init":
                # pb validates keys against exactly these names; all optional.
                fields = [f"{name}: {ann} = ..." for name, ann in self.kwargs_fields(node)]
                return ["self", "*", *fields] if fields else ["self"]
            case "args_init":
                # pb's lambda has no py::arg names: parameters are positional-only.
                fields = [f"{f.pyname}: {self.annotation(f)}" for f in node.fields]
                return ["self", *fields, "/"] if fields else ["self"]
            case "factory_init":
                # py::init(&factory): the factory's own signature (usually none).
                return ["self"]
            case _:
                return ["self"]

    def annotation(self, field: FieldNode) -> str:
        return self.types.map_cx(field.cursor.type)

    def kwargs_fields(self, node: KwargsInitNode) -> list[tuple[str, str]]:
        """(pyname, annotation) per accepted kwarg; flattened fields expanded."""
        out = []
        for field in node.fields:
            if field.spec is not None and field.spec.flatten:
                record = field.cursor.type.get_canonical()
                out += [
                    (self.format_field(nested.spelling), self.types.map_cx(nested.type))
                    for nested in record.get_fields()
                ]
            else:
                out.append((field.pyname, self.annotation(field)))
        return out
