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

        node = self.node
        cursor = self.cursor

        if cursor.is_scoped_enum():
            return self.visit_scoped_enum(cursor)
        
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
        with self.out:
            for child in cursor.get_children():
                self.out(
                    f'.value("{self.format_enum(child.spelling)}", {name}::{child.spelling})'
                )
            self.out(".export_values();")
        self.out()

    def visit_scoped_enum(self, cursor):
        #logger.debug(cursor.spelling)
        name = self.spell(cursor)
        # logger.debug(name)
        pyname = self.format_type(cursor.spelling)
        self.out(f"PYENUM_SCOPED_BEGIN({self.module}, {name}, {pyname})")
        self.out(pyname)
        with self.out:
            for child in cursor.get_children():
                #logger.debug(child.kind) #CursorKind.ENUM_CONSTANT_DECL
                self.out(
                    f'.value("{self.format_enum(child.spelling)}", {name}::{child.spelling})'
                )
            self.out(".export_values();")
        self.out(f"PYENUM_SCOPED_END({self.module}, {name}, {pyname})")
        self.out()
