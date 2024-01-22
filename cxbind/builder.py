from typing import List, Dict, Tuple, Optional, Union, Any, Callable
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .builder_context import BuilderContext
from .entry import Entry
from .node import (
    Node,
    Function,
    Ctor,
    Field,
    Method,
    StructBase,
    Struct,
    Class,
    Enum,
    Typedef,
)

class Builder:
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self, context: BuilderContext):
        super().__init__()
        self.context = context

    @property
    def prefixes(self):
        return self.context.prefixes
    
    @property
    def wrapped(self):
        return self.context.wrapped
    
    @property
    def indent(self):
        return self.context.indentation
    
    @property
    def text(self):
        return self.context.text
    
    @property
    def source(self):
        return self.context.source
    
    @property
    def mapped(self):
        return self.context.mapped
    
    @property
    def target(self):
        return self.context.target
    
    @property
    def module(self):
        return self.context.module
    
    @property
    def flags(self):
        return self.context.flags
    
    @property
    def defaults(self):
        return self.context.defaults

    @property
    def excluded(self):
        return self.context.excluded

    @property
    def overloaded(self):
        return self.context.overloaded
    
    @property
    def entries(self):
        return self.context.entries
    
    @property
    def nodes(self):
        return self.context.nodes
    
    @property
    def node_stack(self):
        return self.context.node_stack
    
    def write(self, text: str):
        self.context.write(text)

    def write_indented(self, text: str):
        self.context.write_indented(text)

    def __call__(self, line=""):
        self.context(line)

    @contextmanager
    def enter(self, node):
        self.context.push_node(node)
        self.context.indent()
        yield node
        self.context.dedent()
        self.context.pop_node()

    def __enter__(self):
        self.context.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.__exit__(exc_type, exc_val, exc_tb)

    def push_node(self, node):
        self.context.push_node(node)

    def pop_node(self):
        self.context.pop_node()

    def indent(self):
        self.context.indent()

    def dedent(self):
        self.context.dedent()

    @property
    def top_node(self):
        return self.context.top_node
    
    def spell(self, node: cindex.Cursor):
        return self.context.spell(node)
    
    def format_field(self, name: str):
        return self.context.format_field(name)
    
    def format_type(self, name: str):
        return self.context.format_type(name)
    
    def format_enum(self, name: str):
        return self.context.format_enum(name)
    
    def arg_type(self, argument):
        return self.context.arg_type(argument)

    def arg_types(self, argument):
        return self.context.arg_types(argument)

    def arg_name(self, argument):
        return self.context.arg_name(argument)
    
    def arg_names(self, arguments: List[cindex.Cursor]):
        return self.context.arg_names(arguments)
    
    def arg_string(self, arguments):
        return self.context.arg_string(arguments)

    def register_entry(self, entry: Entry):
        return self.context.register_entry(entry)

    def lookup_entry(self, key: str) -> Entry:
        return self.context.lookup_entry(key)

    def lookup_node(self, key: str) -> Node:
        return self.context.lookup_node(key)

    def create_builder(self, entry_key: str, cursor: cindex.Cursor = None) -> Node:
        return self.context.create_builder(entry_key, cursor)

    @property
    def scope(self):
        node = self.top_node
        if node is None:
            return self.module
        else:
            return node.pyname

    def module_(self, node: Node):
        if node is None:
            return self.module
        else:
            return node.pyname

    def is_excluded(self, cursor):
        if self.spell(cursor) in self.excluded:
            return True
        if cursor.spelling.startswith("_"):
            return True
        return False

    def is_cursor_mappable(self, cursor):
        if self.is_excluded(cursor):
            return False
        if cursor.access_specifier == cindex.AccessSpecifier.PRIVATE:
            return False
        if cursor.access_specifier == cindex.AccessSpecifier.PROTECTED:
            return False
        if cursor.location.file:
            node_path = Path(cursor.location.file.name)
            return node_path.name in self.mapped
        if cu.is_template(cursor):
            return False
        return True

    def is_rvalue_ref(self, param):
        return param.kind == cindex.TypeKind.RVALUEREFERENCE

    def is_char_ptr(self, cursor):
        if cursor.type.get_canonical().kind == cindex.TypeKind.POINTER:
            ptr = cursor.type.get_canonical().get_pointee().kind
            # logger.debug(f'{ptr}: {cursor.spelling}')
            if ptr == cindex.TypeKind.CHAR_S:
                return True
        return False

    def is_fn_ptr(self, cursor):
        if cursor.type.kind in [cindex.TypeKind.POINTER, cindex.TypeKind.TYPEDEF]:
            ptr = cursor.type.get_canonical().get_pointee().kind
            # logger.debug(f'{ptr}: {cursor.spelling}')
            if ptr == cindex.TypeKind.FUNCTIONPROTO:
                return True
        return False

    def is_forward_declaration(self, cursor):
        definition = cursor.get_definition()

        # If the definition is null, then there is no definition in this translation
        # unit, so this cursor must be a forward declaration.
        if not definition:
            return True
        # If there is a definition, then the forward declaration and the definition
        # are in the same translation unit. This cursor is the forward declaration if
        # it is _not_ the definition.
        return cursor != definition
    
    def visit(self, cursor):
        #logger.debug(f"{cursor.kind} : {cursor.spelling}")
        if not self.is_cursor_mappable(cursor):
            return
        if not cursor.kind in self.actions:
            return
        self.actions[cursor.kind](self, cursor)

    def visit_children(self, cursor):
        for child in cursor.get_children():
            self.visit(child)

    def visit_none(self, cursor):
        logger.debug(f"visit_none: {cursor.spelling}")

    def visit_typedef_decl(self, cursor):
        builder = self.create_builder(f'typedef.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_enum(self, cursor):
        builder = self.create_builder(f'enum.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_field(self, cursor):
        builder = self.create_builder(f'field.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

        self.top_node.add_child(node)

    # TODO: Handle is_deleted_method
    def visit_constructor(self, cursor):
        builder = self.create_builder(f'ctor.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_function(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_method(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_function_or_method(self, cursor):
        builder = self.create_builder(f'function.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_struct(self, cursor):
        builder = self.create_builder(f'struct.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_class(self, cursor):
        builder = self.create_builder(f'class.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()


    def visit_var(self, cursor):
        #logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        pass

    def visit_using_decl(self, cursor):
        #logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        pass
