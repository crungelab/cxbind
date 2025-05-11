from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from ..node import Node
from ..spec import Spec, create_spec

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
    ) -> None:
        super().__init__(context)
        self.name = name
        self.cursor = cursor
        self.node: T_Node = None

    def create_pyname(self, name):
        return self.format_type(name)

    def should_cancel(self):
        '''
        if self.context.visited.get(self.name):
            return True
        '''
        return False

    def find_spec(self):
        key = Node.make_key(self.cursor)
        spec = self.lookup_spec(key)
        return spec

    def build(self) -> T_Node:
        if self.should_cancel():
            return None

        self.create_node()
        spec = self.find_spec()
        if spec is None:
            key = Node.make_key(self.cursor)
            #logger.debug(f"Spec not found for {key}")
            spec = create_spec(key)
        self.node.spec = spec

        self.build_node()
        self.context.visited[self.name] = self.node
        return self.node

    def create_node(self):
        pass

    def build_node(self):
        self.node.pyname = self.create_pyname(self.node.first_name)

        if self.node.spec.exclude:
            raise Exception(f"Node excluded: {self.node.name}")
