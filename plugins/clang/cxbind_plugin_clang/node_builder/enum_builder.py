from loguru import logger

from .node_builder import NodeBuilder
#from ..node import EnumNode, TypedefNode
from ..node import EnumNode


class EnumBuilder(NodeBuilder[EnumNode]):
    def create_node(self):
        self.node = EnumNode(kind='enum', name=self.name, cursor=self.cursor)

    def create_pyname(self, name):
        return self.context.format_enum(name)

    def should_cancel(self):
        '''
        if isinstance(self.top_node, TypedefNode): #TODO: for some reason it's visiting the same node twice when typedef'd
            return True
        '''
        if self.is_forward_declaration(self.cursor):
            return True
        return super().should_cancel()


    def build_node(self):
        super().build_node()
        #logger.debug(f"Building Enum: {self.node.name}")

        self.end_chain()

        node = self.node
        cursor = self.cursor

        name = self.spell(cursor)
        pyname = self.format_type(cursor.spelling)

        #self.out(f'py::enum_<{name}>({self.module}, "{pyname}", py::arithmetic())')
        self.out(f'py::enum_<{name}>({self.scope}, "{pyname}", py::arithmetic())')

        with self.out as out:
            for child in cursor.get_children():
                out(
                    f'.value("{self.format_enum_constant(child.spelling, self.node.first_name)}", {name}::{child.spelling})'
                )
            out(".export_values()")

        self.out(";")
