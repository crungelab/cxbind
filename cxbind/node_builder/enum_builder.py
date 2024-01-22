from loguru import logger

from .node_builder import NodeBuilder
from ..node import Enum, Typedef


class EnumBuilder(NodeBuilder[Enum]):
    def create_node(self):
        self.node = Enum(self.fqname, self.cursor)

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
            fqname = typedef_parent.fqname
            pyname = typedef_parent.pyname
        else:
            fqname = self.spell(cursor)
            pyname = self.format_type(cursor.spelling)

        #TODO: for some reason it's visiting the same enum twice when typedef'd
        if not pyname:
            return
        
        self(
            f'py::enum_<{fqname}>({self.module}, "{pyname}", py::arithmetic())'
        )
        with self:
            for child in cursor.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self()

    def visit_scoped_enum(self, cursor):
        #logger.debug(cursor.spelling)
        fqname = self.spell(cursor)
        # logger.debug(fqname)
        pyname = self.format_type(cursor.spelling)
        self(f"PYENUM_SCOPED_BEGIN({self.module}, {fqname}, {pyname})")
        self(pyname)
        with self:
            for child in cursor.get_children():
                #logger.debug(child.kind) #CursorKind.ENUM_CONSTANT_DECL
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self(f"PYENUM_SCOPED_END({self.module}, {fqname}, {pyname})")
        self()
