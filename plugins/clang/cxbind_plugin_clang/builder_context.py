from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

if TYPE_CHECKING:
    from .node_builder import NodeBuilder

from clang import cindex
from loguru import logger

from cxbind.unit import Unit

from .worker_context import WorkerContext

class BuilderContext(WorkerContext):
    def __init__(self, unit: Unit, **kwargs) -> None:
        super().__init__(unit, **kwargs)

    def create_builder(
        self, entry_key: str, cursor: cindex.Cursor = None
    ) -> "NodeBuilder":
        from .node_builder.node_builder_table import NODE_BUILDER_TABLE
        from .node_builder import NodeBuilder

        kind, name = entry_key.split("/")
        builder_cls: Type[NodeBuilder] = NODE_BUILDER_TABLE[kind]
        builder = builder_cls(self, name, cursor)
        return builder
