from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from ..node import Node

from ..builder import Builder
from ..builder_context import BuilderContext

# Define a generic type variable
T_Node = TypeVar("T_Node", bound=Node)


class NodeBuilder(Builder, Generic[T_Node]):
    def __init__(
        self,
        context: BuilderContext,
        name: str,
        cursor: cindex.Cursor = None,
        # node: Node = None,
    ) -> None:
        super().__init__(context)
        self.name = name
        self.cursor = cursor
        # self.node = node
        self.node: T_Node = None

    def create_pyname(self, name):
        return self.format_type(name)

    def should_cancel(self):
        '''
        if self.context.visited.get(self.name):
            return True
        '''
        return False

    def find_or_create_node(self):
        node = self.lookup_node(self.name)
        if node is None:
            self.create_node()
        else:
            self.node = node

    def build(self) -> T_Node:
        if self.should_cancel():
            return None

        self.find_or_create_node()
        '''
        if self.node is None:
            self.create_node()
        '''

        self.build_node()
        self.context.visited[self.name] = self.node
        return self.node

    def create_node(self):
        pass

    def build_node(self):
        self.node.pyname = self.create_pyname(self.node.first_name)

        if self.node.exclude:
            raise Exception(f"Node excluded: {self.node.name}")
