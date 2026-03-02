from typing import (
    TypeVar,
    Generic,
    List,
    Dict,
    Tuple,
    Optional,
    Union,
    Any,
    Callable,
    Generator,
)
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .worker_context import WorkerContext
from .node import Node, StructuralNode

T_Context = TypeVar("T_Context", bound=WorkerContext)


class Worker(Generic[T_Context]):
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self, context: T_Context) -> None:
        super().__init__()
        self.context = context
        self.session = context.session

    @property
    def unit(self):
        return self.session.unit

    @property
    def prefixes(self) -> list[str]:
        return self.session.prefixes

    @property
    def wrapped(self) -> dict[str, StructuralNode]:
        return self.session.wrapped

    @property
    def mapped(self):
        return self.session.mapped

    @property
    def target(self):
        return self.session.target

    @property
    def module(self):
        return self.session.module

    @property
    def flags(self):
        return self.session.flags

    @property
    def defaults(self):
        return self.session.defaults

    @property
    def excluded(self):
        return self.session.excluded

    @property
    def overloaded(self):
        return self.session.overloaded

    @property
    def node_stack(self):
        return self.session.node_stack

    def push_node(self, node) -> None:
        self.session.push_node(node)

    def pop_node(self) -> Node:
        self.session.pop_node()

    @property
    def top_node(self) -> Optional[Node]:
        return self.session.top_node

    def spell(self, cursor: cindex.Cursor) -> str:
        return self.session.spell(cursor)

    def format_field(self, name: str) -> str:
        return self.session.format_field(name)

    def format_function(self, name: str) -> str:
        return self.session.format_function(name)

    def format_type(self, name: str) -> str:
        return self.session.format_type(name)

    def format_enum_constant(self, name: str, enum_name: str) -> str:
        return self.session.format_enum_constant(name, enum_name)

    def register_node(self, node: Node) -> str:
        return self.session.register_spec(node)

    def lookup_spec(self, key: str) -> Node:
        return self.session.lookup_spec(key)

    @property
    def scope(self) -> str:
        node = self.top_node
        if node.kind == "root":
            return self.module
        else:
            return node.pyname

    def module_(self, node: Node):
        if node.kind == "root":
            return self.module
        else:
            return node.pyname

    def is_overloaded(self, cursor: cindex.Cursor) -> bool:
        return self.spell(cursor) in self.overloaded

    def is_excluded(self, cursor: cindex.Cursor):
        if Node.make_key(cursor) in self.excluded:
            return True
        if self.is_overloaded(cursor):
            key = Node.make_key(cursor, overload=True)
            logger.debug(f"Checking overloaded: {key}")
            if key in self.excluded:
                logger.debug(f"Excluded: {key}")
                return True
        if cursor.spelling.startswith("_"):
            return True
        return False

    def is_cursor_bindable(self, cursor: cindex.Cursor):
        if self.is_excluded(cursor):
            return False
        if cursor.access_specifier == cindex.AccessSpecifier.PRIVATE:
            return False
        if cursor.access_specifier == cindex.AccessSpecifier.PROTECTED:
            return False
        if cu.is_template(cursor.type):
            return False
        if cursor.location.file:
            node_path = Path(cursor.location.file.name)
            mappable = node_path.name in self.mapped
            if not mappable:
                logger.warning(f"Not mappable: {node_path.name}")
                return False

        return True

    def is_rvalue_ref(self, param: cindex.Cursor):
        return param.kind == cindex.TypeKind.RVALUEREFERENCE

    def is_char_ptr(self, cursor: cindex.Cursor):
        if cursor.type.get_canonical().kind == cindex.TypeKind.POINTER:
            ptr = cursor.type.get_canonical().get_pointee().kind
            # logger.debug(f'{ptr}: {cursor.spelling}')
            if ptr == cindex.TypeKind.CHAR_S:
                return True
        return False

    def resolve_type(self, type: cindex.Cursor):
        # If the type is a typedef, resolve it to the actual type it refers to
        while type.kind == cindex.TypeKind.TYPEDEF:
            type = type.get_declaration().underlying_typedef_type
        return type

    def is_function_pointer(self, cursor: cindex.Cursor):
        # logger.debug(f"Checking if {cursor.spelling} is a function pointer")
        # Resolve any typedef or alias and check if the type is a pointer to a function
        type = self.resolve_type(cursor.type)
        # logger.debug(f"Resolved type: {resolved_type.spelling}")
        return (
            type.kind == cindex.TypeKind.POINTER
            and type.get_pointee().kind == cindex.TypeKind.FUNCTIONPROTO
        )

    # TODO:  Might want to pass index to handle multiple unnamed arguments
    def arg_spelling(self, argument: cindex.Cursor):
        if argument.spelling == "":
            return "arg"
        return argument.spelling

    def is_forward_declaration(self, cursor: cindex.Cursor):
        definition = cursor.get_definition()

        # If the definition is null, then there is no definition in this translation
        # unit, so this cursor must be a forward declaration.
        if not definition:
            return True
        # If there is a definition, then the forward declaration and the definition
        # are in the same translation unit. This cursor is the forward declaration if
        # it is _not_ the definition.
        return cursor != definition

    # Function to get the base type name without qualifiers or pointers
    def get_base_type_name(self, typ: cindex.Type):
        # Loop to remove qualifiers like 'const' or 'volatile' and dereference pointers/references
        while True:
            # Remove const/volatile qualifiers
            if typ.is_const_qualified() or typ.is_volatile_qualified():
                typ = typ.get_canonical()

            # If the type is a pointer or reference, dereference it
            if typ.kind == cindex.TypeKind.POINTER:
                typ = typ.get_pointee()
            elif (
                typ.kind == cindex.TypeKind.LVALUEREFERENCE
                or typ.kind == cindex.TypeKind.RVALUEREFERENCE
            ):
                typ = typ.get_pointee()
            else:
                # When no more qualifiers or pointers, break out of the loop
                break

        # Return the base type name
        # return typ.spelling
        return typ.spelling.replace("const ", "").replace("volatile ", "")
