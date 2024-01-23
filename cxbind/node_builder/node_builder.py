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
        node: Node = None,
    ) -> None:
        super().__init__(context)
        self.name = name
        self.cursor = cursor
        self.node = node

    def create_pyname(self, name):
        return self.format_type(name)

    def should_cancel(self):
        pass
        #TODO: Do we need this?
        '''
        if self.node is not None and self.node.visited:
            return True
        '''

    def build(self) -> T_Node:
        if self.should_cancel():
            return None

        if self.node is None:
            self.create_node()

        self.build_node()
        # self.build_children()
        #self.node.visited = True
        return self.node

    def create_node(self):
        pass

    def build_node(self):
        self.node.pyname = self.create_pyname(self.node.first_name)

        if self.node.exclude:
            logger.debug(f"Exclude: {self.node.name}")
            exit()

    def build_children(self):
        pass
        """
        for tf_child in self.tf_node.children:
            child = self.build_child(self.tf_model.nodes[tf_child])
            self.node.add_child(child)
        """

    def build_child(self, cursor: cindex.Cursor) -> Node:
        pass
        """
        from .poly_node_builder import PolyNodeBuilder
        builder = PolyNodeBuilder(self.tf_model, child)
        return builder.build()
        """
