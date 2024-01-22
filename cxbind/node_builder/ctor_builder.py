from .node_builder import NodeBuilder
from ..node import Ctor


class CtorBuilder(NodeBuilder[Ctor]):
    def create_node(self):
        self.node = Ctor(self.fqname, self.cursor)

    def should_cancel(self):
        return super().should_cancel() or not self.is_function_mappable(self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor
        #TODO: This should be in Clang 15.06, but it's not ...
        #if cursor.is_deleted_method():
        #    return
        if self.top_node.readonly:
            return
        self.top_node.has_constructor = True
        arguments = [a for a in cursor.get_arguments()]
        if len(arguments):
            self(
                f"{self.scope}.def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            self(");")
        else:
            self(f"{self.scope}.def(py::init<>());")
