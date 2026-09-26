from loguru import logger

from ...node import EnumNode

from ..py_enum import PyEnum
from ..renderer_registry import PbRendererRegistry
from .node_renderer import NodeRenderer


@PbRendererRegistry.register("enum")
class EnumRenderer(NodeRenderer[EnumNode]):
    def render(self):
        self.end_chain()

        node = self.node
        name = self.spell(node.cursor)
        pyname = node.pyname  # resolved via node.binding
        pyenum = PyEnum.from_node(node, self.format_enum_constant)

        self.out(f'py::enum_<{name}>(_{self.scope}, "{pyname}", py::arithmetic())')

        with self.out as out:
            for constant in pyenum.constants:
                out(f'.value("{constant.name}", {name}::{constant.spelling})')
            # Scoped enums keep their constants scoped, and stripped names
            # would collide in the parent scope: see PyEnum.exported.
            if pyenum.exported:
                out(".export_values()")

        self.out(";")