from loguru import logger
from .node_builder import NodeBuilder
from .method_builder import MethodBuilder
from ..node import CtorNode


class CtorBuilder(MethodBuilder):
    def should_cancel(self):
        if self.top_node is None:
            return True
        return super().should_cancel()

    def create_node(self):
        self.node = CtorNode(kind='ctor', name=self.name, cursor=self.cursor)

    def build_node(self):
        #super().build_node()
        NodeBuilder.build_node(self)
        out = self.out

        if self.top_node.spec.readonly:
            return
        
        self.begin_chain()
        
        self.top_node.has_constructor = True
        arguments = [a for a in self.cursor.get_arguments()]
        if len(arguments):
            out(
                f".def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments, self.node)
            out(")")
        else:
            out(".def(py::init<>())")
