import re
from collections import defaultdict
from typing import Callable, Generic, Hashable, TypeVar

from ...node import Node, FunctionalNode

from ..renderer import Renderer
from ..renderer_registry import PyiRendererRegistry

T_Node = TypeVar("T_Node", bound=Node)

# A stub declaration: (decorators, "def ...: ...") -- hashable for dedup.
Declaration = tuple[tuple[str, ...], str]

# Rough breadth of a parameter type for mypy's overload matching: Any
# accepts everything, and float accepts int. Narrower signatures go first.
_BREADTH = {"Any": 100, "float": 2, "int": 1}
_WORD_RE = re.compile(r"\b(Any|float|int)\b")


def overload_key(node: Node) -> Hashable | None:
    """Nodes with the same key in one scope form a Python overload set."""
    if not isinstance(node, FunctionalNode) or node.mogrified:
        return None
    if node.kind == "ctor":
        return ("ctor",)
    kind = "method" if node.kind == "method" else "function"
    return (kind, node.pyname)


def breadth(declaration: Declaration) -> int:
    _, line = declaration
    params = line.split("(", 1)[1].rsplit(") ->", 1)[0]
    return sum(_BREADTH[m] for m in _WORD_RE.findall(params))


class PyiNodeRenderer(Renderer, Generic[T_Node]):
    def __init__(self, node: T_Node) -> None:
        super().__init__()
        self.node = node

    @property
    def types(self):
        return self.context.types

    def render(self):
        self.render_children(self.node.children)

    def render_children(
        self,
        children: list[Node],
        render_one: Callable[[Node], None] | None = None,
    ) -> None:
        """Render children, emitting each overload set contiguously.

        C++ may interleave overloads (ImGui does); a stub's @overload set
        must be consecutive. Each set renders where its first member was.
        """
        render_one = render_one or self.context.render_node

        groups: dict[Hashable, list[Node]] = defaultdict(list)
        for child in children:
            key = overload_key(child)
            if key is not None:
                groups[key].append(child)

        done: set[Hashable] = set()
        for child in children:
            key = overload_key(child)
            if key is not None and len(groups[key]) > 1:
                if key not in done:
                    done.add(key)
                    self.render_overloads(groups[key])
                continue
            render_one(child)

    def render_overloads(self, nodes: list[Node]) -> None:
        declarations: list[Declaration] = []
        seen: set[Declaration] = set()
        for node in nodes:
            renderer = self.context.create_renderer(node)
            if renderer is None:
                continue
            declaration = renderer.declaration()
            # C++ overloads can collapse to one Python signature
            # (int/unsigned, float/double): keep one.
            if declaration not in seen:
                seen.add(declaration)
                declarations.append(declaration)

        declarations.sort(key=breadth)  # stable: ties keep C++ order

        overloaded = len(declarations) > 1
        if overloaded:
            self.context.add_import("typing", "overload")
        for decorators, line in declarations:
            if overloaded:
                self.out("@overload")
            for decorator in decorators:
                self.out(decorator)
            self.out(line)


# Namespaces don't exist in the Python API: just render their contents.
PyiRendererRegistry.register("namespace")(PyiNodeRenderer)