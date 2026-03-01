from .functional_builder import FunctionalBuilder
from ..node import FunctionNode


class FunctionBuilder(FunctionalBuilder[FunctionNode]):
    def create_node(self):
        self.node = FunctionNode(kind='function', name=self.name, cursor=self.cursor)
