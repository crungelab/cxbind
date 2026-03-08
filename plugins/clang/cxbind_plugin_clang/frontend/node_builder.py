from typing import TYPE_CHECKING, TypeVar, Generic, Dict, List

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ..node import Node

from .builder import Builder
from .builder_context import BuilderContext

T_Node = TypeVar("T_Node", bound=Node)


class NodeBuilder(Builder, Generic[T_Node]):
    def __init__(
        self,
        name: str,
        cursor: cindex.Cursor = None,
        spec: Spec = None,
    ) -> None:
        super().__init__()
        #self.name = name
        self.cursor = cursor
        self.spec = spec or self.find_or_create_spec()
        self.name = self.spec.alias or name
        #self.pyname = self.spec.pyname or self.create_pyname(self.spec.first_name)
        self.node: T_Node = None

    def create_pyname(self, name) -> str:
        return self.format_type(name)

    def should_cancel(self) -> bool:
        return False

    def find_spec(self) -> Spec:
        key = Node.make_key(self.cursor)
        spec = self.lookup_spec(key)
        #spec = self.lookup_spec(self.node.name)
        #spec = self.lookup_spec(self.node.name)
        #spec = self.lookup_spec(self.spell(self.cursor))
        return spec

    def find_or_create_spec(self) -> Spec:
        spec = self.find_spec()
        if spec is None:
            key = Node.make_key(self.cursor)
            #kind = Node.make_kind(self.cursor)
            # logger.debug(f"Spec not found for {key}")
            #spec = create_spec(key, kind)
            spec = create_spec(key)
        return spec

    def get_pyname(self) -> str:
        pyname = self.spec.pyname or self.create_pyname(self.node.first_name)
        return pyname

    def build(self) -> None:
        if self.should_cancel():
            return

        logger.debug(f"Building node: {self.name}")

        self.create_node()

        handled = self.build_node()
        if not handled:
            self.top_node.add_child(self.node)

        #self.current_session.visited[self.name] = self.node

    def create_node(self):
        pass

    def build_node(self):
        self.node.spec = self.spec
        #self.node.pyname = self.pyname
        self.node.pyname = self.get_pyname()

        if self.node.spec.exclude:
            raise Exception(f"Node excluded: {self.node.name}")
