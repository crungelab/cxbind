from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

if TYPE_CHECKING:
    from .node_builder import NodeBuilder

from clang import cindex
from loguru import logger

from .worker_context import WorkerContext
from .session import Session


class BuilderContext(WorkerContext):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create_builder(
        self, entry_key: str, cursor: cindex.Cursor = None
    ) -> "NodeBuilder":
        from .node_builder.node_builder_table import NODE_BUILDER_TABLE
        from .node_builder import NodeBuilder

        kind, name = entry_key.split("/")
        builder_cls: Type[NodeBuilder] = NODE_BUILDER_TABLE[kind]
        builder = builder_cls(self, name, cursor)
        return builder
