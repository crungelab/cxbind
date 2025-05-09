from .function_base_builder import FunctionBaseBuilder
from ..node import MethodNode


class MethodBuilder(FunctionBaseBuilder[MethodNode]):
    def should_cancel(self):
        if self.top_node is None:
            return True
        '''
        if self.top_node is None:
            raise Exception(f"Method with no top node: {self.node.name}")
        '''
        return super().should_cancel()

    def create_node(self):
        self.node = MethodNode(kind='method', name=self.name, cursor=self.cursor)
