from typing import TYPE_CHECKING, Type, Optional
import contextlib
from contextvars import ContextVar

if TYPE_CHECKING:
    from . import NodeBuilder

from clang import cindex
from loguru import logger

from cxbind.unit import Unit

from ..worker_context import WorkerContext
from ..session import Session

current_builder_context: ContextVar[Optional["BuilderContext"]] = ContextVar("current_builder_context", default=None)

class BuilderContext(WorkerContext):
    def __init__(self) -> None:
        super().__init__()
        self.mapped: set[str] = set()

    def make_current(self):
        current_builder_context.set(self)

    @classmethod
    def get_current(cls) -> Optional["BuilderContext"]:
        return current_builder_context.get()

    def create_builder(
        self, entry_key: str, cursor: cindex.Cursor = None
    ) -> "NodeBuilder":
        from .node_builder_table import NODE_BUILDER_TABLE
        from . import NodeBuilder

        kind, name = entry_key.split("@")
        builder_cls: Type[NodeBuilder] = NODE_BUILDER_TABLE[kind]
        builder = builder_cls(name, cursor)
        return builder
