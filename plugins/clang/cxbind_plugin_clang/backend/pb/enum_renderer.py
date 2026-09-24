from clang import cindex
from loguru import logger

from .node_renderer import NodeRenderer

from ..renderer_registry import PbRendererRegistry

from ...node import EnumNode


@PbRendererRegistry.register("enum")
class EnumRenderer(NodeRenderer[EnumNode]):
    def render(self):
        # logger.debug(f"Building Enum: {self.node.name}")

        self.end_chain()

        node = self.node
        cursor = node.cursor

        name = self.spell(cursor)
        pyname = node.pyname  # resolved via node.binding

        self.out(f'py::enum_<{name}>(_{self.scope}, "{pyname}", py::arithmetic())')

        with self.out as out:
            for child in cursor.get_children():
                # Skip attributes and other non-constant children.
                if child.kind != cindex.CursorKind.ENUM_CONSTANT_DECL:
                    continue
                # Prefix stripping uses the C++ enum name, so constants stay
                # stable even if the registry renames the enum.
                out(
                    f'.value("{self.format_enum_constant(child.spelling, node.first_name)}", {name}::{child.spelling})'
                )
            # Scoped enums keep their constants scoped; exporting them would
            # silently overwrite same-named constants in the parent scope.
            if not cursor.is_scoped_enum():
                out(".export_values()")

        self.out(";")
