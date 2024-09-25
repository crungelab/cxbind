from loguru import logger

from .node_builder import NodeBuilder
from ..node import EnumNode, TypedefNode


class EnumBuilder(NodeBuilder[EnumNode]):
    def create_node(self):
        self.node = EnumNode(name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.context.format_enum(name)

    def should_cancel(self):
        return super().should_cancel() or self.is_forward_declaration(self.cursor)

    def build_node(self):
        super().build_node()
        logger.debug(f"Building Enum: {self.node.name}")

        if self.chaining:
            self.end_chain()
        self.chaining = True

        node = self.node
        cursor = self.cursor
        
        typedef_parent = self.top_node if isinstance(self.top_node, TypedefNode) else None

        if typedef_parent:
            name = typedef_parent.name
            pyname = typedef_parent.pyname
        else:
            name = self.spell(cursor)
            pyname = self.format_type(cursor.spelling)

        #TODO: for some reason it's visiting the same enum twice when typedef'd
        if not pyname:
            return
        
        self.out(
            f'py::enum_<{name}>({self.module}, "{pyname}", py::arithmetic())'
        )
        with self.out as out:
            for child in cursor.get_children():
                out(
                    f'.value("{self.format_enum_constant(child.spelling, self.node.first_name)}", {name}::{child.spelling})'
                )
            out(".export_values()")
        self.end_chain()
        self.out()
