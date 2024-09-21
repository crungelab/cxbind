from loguru import logger
from .function_base_builder import FunctionBaseBuilder
from ..node import CtorNode


class CtorBuilder(FunctionBaseBuilder[CtorNode]):
    def should_cancel(self):
        if self.top_node is None:
            return True
        return super().should_cancel()

    def create_node(self):
        self.node = CtorNode(name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        #TODO: This should be in Clang 15.06, but it's not ...
        #if cursor.is_deleted_method():
        #    return
        '''
        if not self.top_node:
            logger.debug(f"no top node for {self.name}")
            return
        '''
        if self.top_node.readonly:
            return
        self.top_node.has_constructor = True
        arguments = [a for a in self.cursor.get_arguments()]
        if len(arguments):
            self.out(
                f"{self.scope}.def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            self.out(");")
        else:
            self.out(f"{self.scope}.def(py::init<>());")
