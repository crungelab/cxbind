from . import StructBaseBuilder
from ..node import ClassNode


class ClassBuilder(StructBaseBuilder[ClassNode]):
    def create_node(self):
        self.node = ClassNode(kind='class', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        self.end_chain()

        #self.out(f"PYCLASS_BEGIN({self.module}, {node.name}, {node.pyname} {extra})")
        #self.out(f"PYCLASS({self.module}, {node.name}, {node.pyname} {extra})")
        '''
        _name(_module, #_name); \
        registry.on(_module, #_name, _name); \
        _name \
        '''
        extra = f",{node.holder}<{node.name}>" if node.holder else ""

        self.out(f'py::class_<{node.name}{extra}> {node.pyname}({self.module}, "{node.pyname}");')
        self.out(f'registry.on({self.module}, "{node.pyname}", {node.pyname});')

        with self.enter(node):
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        self.end_chain()
        #self.out(f"PYCLASS_END({self.module}, {node.name}, {node.pyname})")
        #self.out()
