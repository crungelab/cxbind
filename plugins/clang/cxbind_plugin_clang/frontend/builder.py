from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator
from pathlib import Path
from contextlib import contextmanager

from loguru import logger
from clang import cindex

from cxbind.entry import EntryKey

from .build_context import BuildContext
from ..worker import Worker


class Builder(Worker[BuildContext]):
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self):
        super().__init__()

    @property
    def current_context(self) -> BuildContext:
        return BuildContext.get_current()

    @property
    def mapped(self):
        return self.current_context.mapped

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.push_node(node)
        yield node
        self.pop_node()

    def build(self) -> None:
        raise NotImplementedError("Builder.build must be implemented in subclasses")

    def create_builder(self, entry_key: EntryKey, cursor: cindex.Cursor = None) -> "Builder":
        return self.current_context.create_builder(entry_key, cursor)

    def visit(self, cursor: cindex.Cursor):
        if not self.is_cursor_bindable(cursor):
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

    def visit_translation_unit(self, cursor: cindex.Cursor):
        self.visit_children(cursor)

    def visit_children(self, cursor: cindex.Cursor):
        for child in cursor.get_children():
            self.visit(child)

    def visit_none(self, cursor: cindex.Cursor):
        logger.debug(f"visit_none: {cursor.spelling}")

    def visit_typedef_decl(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="typedef", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_enum(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="enum", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_field(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="field", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_constructor(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="ctor", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_function(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="function", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_function_template(self, cursor: cindex.Cursor):
        sp = cursor.semantic_parent
        logger.debug(f"Function template semantic parent: {sp.spelling}")
        lp = cursor.lexical_parent
        logger.debug(f"Function template lexical parent: {lp.spelling}")


        if sp != lp:
            # Ignore function templates that are not defined in the same scope as they are declared
            logger.debug(
                f"Skipping function template declared in a different scope: {cursor.spelling}"
            )
            return

        builder = self.create_builder(
            EntryKey(kind="function_template", name=self.spell(cursor)), cursor=cursor
        )
        builder.build()

    def visit_method(self, cursor: cindex.Cursor):
        if cursor.semantic_parent != cursor.lexical_parent:
            # Ignore methods that are not defined in the same scope as they are declared
            logger.debug(
                f"Skipping method declared in a different scope: {cursor.spelling}"
            )
            return
        builder = self.create_builder(EntryKey(kind="method", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_struct(self, cursor: cindex.Cursor):
        name = self.spell(cursor)
        logger.debug(f"Struct name: '{name}'")
        if "unnamed struct" in name:
            logger.debug(
                f"Skipping anonymous struct: {name}"
            )  # TODO: Handle this better
            return
        builder = self.create_builder(EntryKey(kind="struct", name=name), cursor=cursor)
        builder.build()

    """
    def visit_struct(self, cursor: cindex.Cursor):
        name = self.spell(cursor)
        logger.debug(f"Struct name: '{name}'")
        if "unnamed struct" in name:
            logger.debug(f"Anonymous struct detected: {name}")
            name = self.session.camel(cu.anonymous_struct_name(cursor))
            logger.debug(f"Renamed to: {name}")
        builder = self.create_builder(f"struct@{name}", cursor=cursor)
        builder.build()
    """

    def visit_class(self, cursor: cindex.Cursor):
        builder = self.create_builder(EntryKey(kind="class", name=self.spell(cursor)), cursor=cursor)
        builder.build()

    def visit_class_template(self, cursor: cindex.Cursor):
        builder = self.create_builder(
            EntryKey(kind="class_template", name=self.spell(cursor)), cursor=cursor
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
