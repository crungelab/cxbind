from clang import cindex

from . import StructBaseBuilder
from ..node import StructNode, FieldNode


class StructBuilder(StructBaseBuilder[StructNode]):
    def create_node(self):
        self.node = StructNode(kind="struct", name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        # Handle the case of a struct with one enum child
        children = list(cursor.get_children())  # it's an iterator
        is_enum_struct = False
        # TODO: Might be more than one enum child?
        if len(children) == 1:
            first_child = children[0]
            is_enum_struct = first_child.kind == cindex.CursorKind.ENUM_DECL
        if is_enum_struct:
            self.visit_children(cursor)
            return

        with self.enter(node):
            self.visit_children(cursor)

