from clang import cindex

from . import StructBaseRenderer
from ...node import StructNode, FieldNode


class StructRenderer(StructBaseRenderer[StructNode]):
    def render(self):
        node = self.node
        self.end_chain()

        # TODO: Don't use the base class for now.  Explicit definition in Node?
        """
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
        """
        self.out(
            f'py::class_<{node.name}> {node.pyname}({self.module}, "{node.pyname}");'
        )
        self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        with self.enter(node):
            super().render()

            if node.spec.gen_init:
                self.gen_init()
            elif node.spec.gen_kw_init:
                self.gen_kw_init()

        self.end_chain()
