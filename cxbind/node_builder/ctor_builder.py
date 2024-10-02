from loguru import logger
#from .function_base_builder import FunctionBaseBuilder
from .node_builder import NodeBuilder
from .method_builder import MethodBuilder
from ..node import CtorNode


#class CtorBuilder(FunctionBaseBuilder[CtorNode]):
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

        if self.top_node.readonly:
            return
        
        if not self.chaining:
            self.begin_chain()
        else:
            out()

        self.top_node.has_constructor = True
        arguments = [a for a in self.cursor.get_arguments()]
        if len(arguments):
            out(
                f".def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            out(")")
        else:
            out(".def(py::init<>())")
            #out()

    '''
    def build_node(self):
        super().build_node()
        if self.top_node.readonly:
            return
        self.top_node.has_constructor = True
        arguments = [a for a in self.cursor.get_arguments()]
        if len(arguments):
            self.out(
                f".def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            self.out(")")
        else:
            self.out(f".def(py::init<>())")
    '''