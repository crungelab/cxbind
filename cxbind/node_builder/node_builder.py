from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from ..node import Node
from ..entry import Entry

from ..builder import Builder
from ..builder_context import BuilderContext

# Define a generic type variable
T_Node = TypeVar("T_Node", bound=Node)


class NodeBuilder(Builder, Generic[T_Node]):
    def __init__(self, context: BuilderContext, fqname: str, cursor: cindex.Cursor = None, entry: Entry=None) -> None:
        super().__init__(context)
        self.fqname = fqname
        self.cursor = cursor
        self.entry = entry
        self.node: T_Node = None

    def create_pyname(self, name):
        return self.format_type(name)

    def should_cancel(self):
        if self.lookup_node(self.fqname) is not None:
            return True

    def build(self) -> T_Node:
        if self.should_cancel():
            return None
                
        self.create_node()

        self.build_node()
        #self.build_children()
        return self.node

    def create_node(self):
        pass

    def build_node(self):
        if self.entry is not None:
            self.node.__dict__.update(self.entry.model_dump())
        self.node.pyname = self.create_pyname(self.node.name)

        if self.node.exclude:
            logger.debug(f"Exclude: {self.node.fqname}")
            exit()


    def build_children(self):
        pass
        '''
        for tf_child in self.tf_node.children:
            child = self.build_child(self.tf_model.nodes[tf_child])
            self.node.add_child(child)
        '''

    def build_child(self, cursor: cindex.Cursor) -> Node:
        pass
        '''
        from .poly_node_builder import PolyNodeBuilder
        builder = PolyNodeBuilder(self.tf_model, child)
        return builder.build()
        '''
