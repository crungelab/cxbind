from loguru import logger

from .node_builder import NodeBuilder
from ..node import Enum, Typedef


class EnumBuilder(NodeBuilder[Enum]):
    def create_node(self):
        self.node = Enum(self.name, self.cursor)

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
        
        typedef_parent = self.top_node if isinstance(self.top_node, Typedef) else None

        if typedef_parent:
            name = typedef_parent.name
            pyname = typedef_parent.pyname
        else:
            name = self.spell(cursor)
            pyname = self.format_type(cursor.spelling)

        #TODO: for some reason it's visiting the same enum twice when typedef'd
        if not pyname:
            return
        
        self(
            f'py::enum_<{name}>({self.module}, "{pyname}", py::arithmetic())'
        )
        with self:
            for child in cursor.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {name}::{child.spelling})'
                )
            self(".export_values();")
        self()

    def visit_scoped_enum(self, cursor):
        #logger.debug(cursor.spelling)
        name = self.spell(cursor)
        # logger.debug(name)
        pyname = self.format_type(cursor.spelling)
        self(f"PYENUM_SCOPED_BEGIN({self.module}, {name}, {pyname})")
        self(pyname)
        with self:
            for child in cursor.get_children():
                #logger.debug(child.kind) #CursorKind.ENUM_CONSTANT_DECL
                self(
                    f'.value("{self.format_enum(child.spelling)}", {name}::{child.spelling})'
                )
            self(".export_values();")
        self(f"PYENUM_SCOPED_END({self.module}, {name}, {pyname})")
        self()
