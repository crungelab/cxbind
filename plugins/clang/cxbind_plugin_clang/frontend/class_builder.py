from . import StructBaseBuilder
from ..node import ClassNode


class ClassBuilder(StructBaseBuilder[ClassNode]):
    def create_node(self):
        self.node = ClassNode(kind='class', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()

        node = self.node
        cursor = self.cursor

        with self.enter(node):
            self.visit_children(cursor)
