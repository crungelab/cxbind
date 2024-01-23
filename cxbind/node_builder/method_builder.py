from .function_base_builder import FunctionBaseBuilder
from ..node import MethodNode


class MethodBuilder(FunctionBaseBuilder[MethodNode]):
    def create_node(self):
        self.node = MethodNode(name=self.name, cursor=self.cursor)
