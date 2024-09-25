from .function_base_builder import FunctionBaseBuilder
from ..node import FunctionNode


class FunctionBuilder(FunctionBaseBuilder[FunctionNode]):
    def create_node(self):
        self.node = FunctionNode(name=self.name, cursor=self.cursor)
