from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from .node import Node, FunctionNode, CtorNode, FieldNode, MethodNode, StructOrClassNode, StructNode, ClassNode, EnumNode, TypedefNode
from .entry import Entry, FunctionEntry, CtorEntry, FieldEntry, MethodEntry, StructEntry, ClassEntry, EnumEntry, TypedefEntry

from .context import GeneratorContext

# Define a generic type variable
T_Node = TypeVar("T_Node", bound=Node)


class NodeBuilder(Generic[T_Node]):
    def __init__(self, context: GeneratorContext, fqname: str, cursor: cindex.Cursor = None, entry: Entry=None) -> None:
        self.context = context
        self.fqname = fqname
        self.cursor = cursor
        self.entry = entry

        self.node: T_Node = None

    def create_pyname(self, name):
        return self.context.format_type(name)

    def build(self) -> T_Node:
        self.create_node()
        self.build_node()
        #self.build_children()
        return self.node

    def create_node(self):
        #self.node = Node()
        pass

    def build_node(self):
        if self.entry is not None:
            self.node.__dict__.update(self.entry.model_dump())
        self.node.pyname = self.create_pyname(self.node.name)

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

class FunctionNodeBuilder(NodeBuilder[FunctionNode]):
    def create_node(self):
        self.node = FunctionNode(self.fqname, self.cursor)

#CtorNode
class CtorNodeBuilder(NodeBuilder[CtorNode]):
    def create_node(self):
        self.node = CtorNode(self.fqname, self.cursor)

#FieldNode
class FieldNodeBuilder(NodeBuilder[FieldNode]):
    def create_node(self):
        self.node = FieldNode(self.fqname, self.cursor)
    def create_pyname(self, name):
        return self.context.format_field(name)

#MethodNode
class MethodNodeBuilder(NodeBuilder[MethodNode]):
    def create_node(self):
        self.node = MethodNode(self.fqname, self.cursor)

#StructOrClassNode
class StructOrClassNodeBuilder(NodeBuilder[StructOrClassNode]):
    def create_node(self):
        self.node = StructOrClassNode(self.fqname, self.cursor)

#StructNode
class StructNodeBuilder(NodeBuilder[StructNode]):
    def create_node(self):
        self.node = StructNode(self.fqname, self.cursor)

#ClassNode
class ClassNodeBuilder(NodeBuilder[ClassNode]):
    def create_node(self):
        self.node = ClassNode(self.fqname, self.cursor)

#EnumNode
class EnumNodeBuilder(NodeBuilder[EnumNode]):
    def create_node(self):
        self.node = EnumNode(self.fqname, self.cursor)
    def create_pyname(self, name):
        return self.context.format_enum(name)

#TypedefNode
class TypedefNodeBuilder(NodeBuilder[TypedefNode]):
    def create_node(self):
        self.node = TypedefNode(self.fqname, self.cursor)