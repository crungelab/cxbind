from typing import TYPE_CHECKING, TypeVar, Generic

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, create_spec

from ..node import Node
from ..pyname_registry import PyBinding, PyKind

from .builder import Builder
from .build_context import BuildContext

T_Node = TypeVar("T_Node", bound=Node)


class NodeBuilder(Builder, Generic[T_Node]):
    # Kind of Python name this builder registers with the session's pyname
    # registry. None means the node's pyname is assigned directly and is not
    # tracked by the registry (no Python name of its own, or not yet migrated).
    py_kind: PyKind | None = None

    def __init__(
        self,
        name: str,
        cursor: cindex.Cursor = None,
        spec: Spec = None,
    ) -> None:
        super().__init__()
        self.cursor = cursor
        self.spec = spec or self.find_or_create_spec()
        self.name = self.spec.alias or name
        self.node: T_Node = None

    # ------------------------------------------------------------------
    # Naming
    # ------------------------------------------------------------------

    def create_pyname(self, name: str) -> str:
        """Format a C++ name into a provisional pyname. Pure: no registration."""
        return self.format_type(name)

    def get_py_kind(self) -> PyKind | None:
        return self.py_kind

    def scope_binding(self) -> PyBinding | None:
        """The binding of the Python scope this node is declared in; None = module."""
        top = self.top_node
        return getattr(top, "binding", None) if top is not None else None

    def register_binding(self) -> None:
        explicit = bool(self.spec.pyname)
        base = self.spec.pyname or self.create_pyname(self.node.first_name)

        kind = self.get_py_kind()
        if kind is None:
            self.node.pyname = base  # untracked: legacy path
            return

        self.node.binding = self.session.pynames.add(
            self.node, kind, self.scope_binding(), base, explicit=explicit
        )

    # ------------------------------------------------------------------

    def should_cancel(self) -> bool:
        return False

    def find_spec(self) -> Spec:
        key = Node.make_key(self.cursor)
        spec = self.lookup_spec(key)
        return spec

    def find_or_create_spec(self) -> Spec:
        spec = self.find_spec()
        if spec is None:
            key = Node.make_key(self.cursor)
            spec = create_spec(key)
        return spec

    def build(self) -> None:
        if self.should_cancel():
            return

        logger.debug(f"Building node: {self.name}")

        self.create_node()

        handled = self.build_node()
        self.register_node()
        if not handled:
            self.top_node.add_child(self.node)

    def create_node(self):
        pass

    def register_node(self):
        self.runner.register_node(self.node)

    def build_node(self):
        self.node.spec = self.spec

        # Check exclusion before registering, so excluded nodes never
        # participate in name resolution.
        if self.node.spec.exclude:
            raise Exception(f"Node excluded: {self.node.name}")

        self.register_binding()
