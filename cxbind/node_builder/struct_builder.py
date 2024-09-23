from clang import cindex

from . import StructBaseBuilder
from ..node import StructNode, FieldNode


class StructBuilder(StructBaseBuilder[StructNode]):
    def create_node(self):
        self.node = StructNode(name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        name = node.name
        pyname = node.pyname

        #TODO: Shouldn't need this?
        if not pyname:
            #return
            raise ValueError(f"Missing pyname for {name}")

        #logger.debug(entry)
        children = list(cursor.get_children())  # it's an iterator
        wrapped = False
        # Handle the case of a struct with one enum child
        if len(children) == 1:
            first_child = children[0]
            wrapped = first_child.kind == cindex.CursorKind.ENUM_DECL
        if not wrapped:
            base = None
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                    base = child
            if base:
                basename = self.spell(base)
                self.out(f"PYSUBCLASS_BEGIN({self.module}, {name}, {basename}, {pyname})")
            else:
                #self.out(f"PYCLASS_BEGIN({self.module}, {name}, {pyname})")
                self.out(f"PYCLASS({self.module}, {name}, {pyname})")
        with self.enter(node):
            #TODO: this is a can of worms trying to map substructures.  Might be worth it if I can figure it out.
            # May add a flag to the yaml to indicate whether to map substructures or not.  example: traverse: shallow|deep
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        '''
        if not wrapped:
            self.out(f"PYCLASS_END({self.module}, {name}, {pyname})")
        '''
        self.out(";")