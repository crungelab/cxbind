from clang import cindex

from . import StructBaseBuilder
from ..node import StructNode, FieldNode


class StructBuilder(StructBaseBuilder[StructNode]):
    def create_node(self):
        self.node = StructNode(kind='struct', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        self.end_chain()

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

        #TODO: Don't use the base class for now.  Explicit definition in Node?
        '''
        base = None
        for child in cursor.get_children():
            if child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                base = child
        if base:
            basename = self.spell(base)
            self.out(f'py::class_<{node.name}, {basename}> {node.pyname}({self.module}, "{node.pyname}");')
            self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        else:
            self.out(f'py::class_<{node.name}> {node.pyname}({self.module}, "{node.pyname}");')
            self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')
        '''
        self.out(f'py::class_<{node.name}> {node.pyname}({self.module}, "{node.pyname}");')
        self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        with self.enter(node):
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        self.end_chain()
        #self.out()