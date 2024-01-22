from .function_base_builder import FunctionBaseBuilder
from ..node import Method


class MethodBuilder(FunctionBaseBuilder[Method]):
    def create_node(self):
        self.node = Method(self.fqname, self.cursor)
