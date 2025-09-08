from loguru import logger

from .node_renderer import NodeRenderer
from ...node import EnumNode


class EnumRenderer(NodeRenderer[EnumNode]):
    def render(self):
        #logger.debug(f"Building Enum: {self.node.name}")

        self.end_chain()

        node = self.node
        cursor = node.cursor

        name = self.spell(cursor)
        pyname = self.format_type(cursor.spelling)

        self.out(f'py::enum_<{name}>({self.scope}, "{pyname}", py::arithmetic())')

        with self.out as out:
            for child in cursor.get_children():
                out(
                    f'.value("{self.format_enum_constant(child.spelling, node.first_name)}", {name}::{child.spelling})'
                )
            out(".export_values()")

        self.out(";")
