from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .builder_context import BuilderContext
from .node import Node, StructBaseNode
from .worker import Worker


class Builder(Worker[BuilderContext]):
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self, context: BuilderContext):
        super().__init__(context)

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.push_node(node)
        yield node
        self.pop_node()

    def create_builder(self, entry_key: str, cursor: cindex.Cursor = None) -> "Builder":
        return self.context.create_builder(entry_key, cursor)

    def visit(self, cursor: cindex.Cursor):
        if not self.is_cursor_mappable(cursor):
            return
        if not cursor.kind in self.actions:
            return
        # logger.debug(f"{cursor.kind} : {cursor.spelling}")
        logger.debug(
            f"Visiting {cursor.spelling} kind={cursor.kind} type={cursor.type.spelling}"
        )
        # logger.debug(f"canonical_type={cursor.type.get_canonical().spelling}")
        # logger.debug(f"canonical_kind={cursor.type.get_canonical().kind}")

        self.actions[cursor.kind](self, cursor)

    def visit_children(self, cursor: cindex.Cursor):
        for child in cursor.get_children():
            self.visit(child)

    def visit_none(self, cursor: cindex.Cursor):
        logger.debug(f"visit_none: {cursor.spelling}")

    def visit_typedef_decl(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"typedef/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_enum(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"enum/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_field(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"field/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_constructor(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"ctor/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_function(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"function/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_method(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"method/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_struct(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"struct/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_class(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"class/{self.spell(cursor)}", cursor=cursor)
        builder.build()

    def visit_class_template(self, cursor: cindex.Cursor):
        builder = self.create_builder(
            f"class_template/{self.spell(cursor)}", cursor=cursor
        )
        builder.build()

    def visit_var(self, cursor: cindex.Cursor):
        logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        pass
        # raise NotImplementedError

    def visit_using_decl(self, cursor: cindex.Cursor):
        logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        # pass
        raise NotImplementedError
