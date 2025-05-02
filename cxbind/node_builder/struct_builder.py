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

        name = node.name
        pyname = node.pyname

        #TODO: Shouldn't need this?
        if not pyname:
            raise ValueError(f"Missing pyname for {name}")

        '''
        if self.chaining:
            self.end_chain()
        self.chaining = True
        '''
        #self.begin_chain()
        self.end_chain()
        #self.begin_chain(emit_scope=False)

        #logger.debug(entry)
        children = list(cursor.get_children())  # it's an iterator
        wrapped = False
        # Handle the case of a struct with one enum child
        if len(children) == 1:
            first_child = children[0]
            wrapped = first_child.kind == cindex.CursorKind.ENUM_DECL

        if not wrapped:
            #TODO: Don't use the base class for now.  Explicit definition in Node?
            '''
            base = None
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                    base = child
            if base:
                basename = self.spell(base)
                #self.out(f"PYSUBCLASS_BEGIN({self.module}, {name}, {basename}, {pyname})")
                #define PYSUBCLASS_BEGIN(_module, _class, _base, _name) py::class_<_class, _base> _name(_module, #_name);
                self.out(f'py::class_<{node.name}, {basename}> {node.pyname}({self.module}, "{node.pyname}");')
                self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

            else:
                #self.out(f"PYCLASS_BEGIN({self.module}, {name}, {pyname})")
                #self.out(f"PYCLASS({self.module}, {name}, {pyname})")
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

        '''
        if not wrapped:
            self.out(f"PYCLASS_END({self.module}, {name}, {pyname})")
        '''

        self.end_chain()
        #self.out()