from typing import TypeVar, Generic, Dict, Optional, Callable
from pathlib import Path

from loguru import logger
from clang import cindex

from . import cu
from .session import Session
from .worker_context import WorkerContext
from .pod import Pod
from .node import Node, StructuralNode

T_Context = TypeVar("T_Context", bound=WorkerContext)


class Worker(Generic[T_Context]):
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self) -> None:
        super().__init__()

    @property
    def session(self) -> Session:
        return Session.get_current()
    
    @property
    def pod(self) -> Pod:
        return Pod.get_current()

    # ------------------------------------------------------------------
    # Session property pass-throughs
    # ------------------------------------------------------------------

    """
    @property
    def unit(self):
        return self.current_session.unit
    """
    
    @property
    def prefixes(self) -> list[str]:
        return self.session.prefixes

    @property
    def wrapped(self) -> dict[str, StructuralNode]:
        return self.session.wrapped

    """
    @property
    def mapped(self):
        return self.current_session.mapped
    """
    
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

    @property
    def top_node(self) -> Optional[Node]:
        return self.session.top_node

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def push_node(self, node) -> None:
        self.session.push_node(node)

    def pop_node(self) -> Node:
        self.session.pop_node()

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Spec / registry
    # ------------------------------------------------------------------

    def register_node(self, node: Node) -> str:
        return self.session.register_spec(node)

    def lookup_spec(self, key: str) -> Node:
        return self.session.lookup_spec(key)

    # ------------------------------------------------------------------
    # Scope helpers
    # ------------------------------------------------------------------

    @property
    def scope(self) -> str:
        node = self.top_node
        return self.module if node.kind == "root" else node.pyname

    def module_(self, node: Node) -> str:
        return self.module if node.kind == "root" else node.pyname

    # ------------------------------------------------------------------
    # Cursor / type predicates
    # ------------------------------------------------------------------

    def is_overloaded(self, cursor: cindex.Cursor) -> bool:
        return self.spell(cursor) in self.overloaded

    def is_excluded(self, cursor: cindex.Cursor) -> bool:
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

    def is_cursor_bindable(self, cursor: cindex.Cursor) -> bool:
        if self.is_excluded(cursor):
            return False
        if cursor.access_specifier in (
            cindex.AccessSpecifier.PRIVATE,
            cindex.AccessSpecifier.PROTECTED,
        ):
            return False
        if cu.is_template(cursor.type):
            return False

        if cursor.location.file:
            return self.is_cursor_mappable(cursor)

        return True

    def is_cursor_mappable(self, cursor: cindex.Cursor) -> bool:
        node_path = Path(cursor.location.file.name)
        name = node_path.name
        mapped = self.mapped
        name_in_mapped = name in mapped

        """
        if name_in_mapped:
            logger.debug(f"Node: {cursor.spelling} path name: {name} is in mapped: {mapped}")
        else:
            logger.debug(f"Node: {cursor.spelling} path name: {name} is not in mapped: {mapped}")
        """

        """
        logger.debug(f"Node path name: {name}")
        logger.debug(f"Mapped: {mapped}")

        logger.debug(f"type(name)={type(name)} type(mapped)={type(mapped)}")
        logger.debug(f"name == next(iter(mapped))? {name == next(iter(mapped))}")
        logger.debug(f"any(x == name for x in mapped)? {any(x == name for x in mapped)}")
        logger.debug(f"name in mapped? {name in mapped}")

        # hash diagnostics (only works if elements are hashable, which strings are)
        first = next(iter(mapped))
        logger.debug(f"hash(name)={hash(name)} hash(first)={hash(first)}")
        logger.debug(f"id(name)={id(name)} id(first)={id(first)}")  # ids can differ; value equality matters
        """

        return name_in_mapped

    """
    def is_cursor_bindable(self, cursor: cindex.Cursor) -> bool:
        if self.is_excluded(cursor):
            return False
        if cursor.access_specifier in (
            cindex.AccessSpecifier.PRIVATE,
            cindex.AccessSpecifier.PROTECTED,
        ):
            return False
        if cu.is_template(cursor.type):
            return False

        if cursor.location.file:
            node_path = Path(cursor.location.file.name)
            logger.debug(f"Node path name: {node_path.name}")
            logger.debug(f"Mapped: {self.mapped}")

            logger.debug(f"Node path repr: {repr(node_path.name)}")
            logger.debug(f"Mapped repr: {[repr(x) for x in self.mapped]}")

            return node_path.name in self.mapped

        return True
    """

    def is_rvalue_ref(self, param: cindex.Type) -> bool:
        return param.kind == cindex.TypeKind.RVALUEREFERENCE

    def is_char_ptr(self, cursor: cindex.Cursor) -> bool:
        canonical = cursor.type.get_canonical()
        return (
            canonical.kind == cindex.TypeKind.POINTER
            and canonical.get_pointee().kind == cindex.TypeKind.CHAR_S
        )

    def is_function_pointer(self, cursor: cindex.Cursor) -> bool:
        t = self._unwrap_typedefs(cursor.type)
        return (
            t.kind == cindex.TypeKind.POINTER
            and t.get_pointee().kind == cindex.TypeKind.FUNCTIONPROTO
        )

    def is_forward_declaration(self, cursor: cindex.Cursor) -> bool:
        definition = cursor.get_definition()
        return (not definition) or (cursor != definition)

    # ------------------------------------------------------------------
    # Type resolution helpers
    # ------------------------------------------------------------------

    def _unwrap_typedefs(self, t: cindex.Type) -> cindex.Type:
        """Fully unwrap typedef chains to reach the underlying type.
        Use this only when you need the concrete type kind (e.g. function pointer
        detection). Do NOT use when you want to preserve the typedef name."""
        while t.kind == cindex.TypeKind.TYPEDEF:
            t = t.get_declaration().underlying_typedef_type
        return t

    # Keep old name as an alias so existing call-sites don't break.
    resolve_type = _unwrap_typedefs

    def typedef_spelling(self, t: cindex.Type) -> Optional[str]:
        """Return the typedef name if `t` is a typedef whose spelling contains
        no unresolved template placeholders, otherwise return None.

        This is the fix for uint32_t (and similar stdint / platform typedefs)
        being collapsed to their canonical form (e.g. 'unsigned int').
        """
        if t.kind != cindex.TypeKind.TYPEDEF:
            return None
        spelling = t.spelling
        if "type-parameter" in spelling:
            return None
        # Strip leading const/volatile so callers get a clean name.
        return spelling.replace("const ", "").replace("volatile ", "").strip()

    def strip_qualifiers(self, name: str) -> str:
        return name.replace("const ", "").replace("volatile ", "").strip()

    def get_base_type_name(self, typ: cindex.Type) -> str:
        """Return the base type name, stripping qualifiers and pointer/reference
        indirections. Typedef names (e.g. uint32_t) are preserved."""
        while True:
            if typ.is_const_qualified() or typ.is_volatile_qualified():
                typ = typ.get_canonical()
            if typ.kind in (
                cindex.TypeKind.POINTER,
                cindex.TypeKind.LVALUEREFERENCE,
                cindex.TypeKind.RVALUEREFERENCE,
            ):
                typ = typ.get_pointee()
            else:
                break
        return self.strip_qualifiers(typ.spelling)

    def get_base_type(self,t: cindex.Type) -> cindex.Type:
        # Resolve typedefs
        t = t.get_canonical()

        # Strip qualifiers
        #t = t.get_unqualified_type()

        # Strip pointers and references
        while t.kind in (
            cindex.TypeKind.POINTER,
            cindex.TypeKind.LVALUEREFERENCE,
            cindex.TypeKind.RVALUEREFERENCE,
        ):
            t = t.get_pointee()
            #t = t.get_unqualified_type()

        # Strip arrays
        while t.kind in (
            cindex.TypeKind.CONSTANTARRAY,
            cindex.TypeKind.INCOMPLETEARRAY,
            cindex.TypeKind.VARIABLEARRAY,
        ):
            t = t.get_array_element_type()
            #t = t.get_unqualified_type()

        return t

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def make_arg_name(self, argument: cindex.Cursor) -> str:
        return argument.spelling or "arg"
    
    def is_wrapped_type(self, cursor: cindex.Cursor) -> bool:
        type_name = self.get_base_type_name(cursor)
        #logger.debug(f"type_name: {type_name}")
        if type_name in self.wrapped:
            logger.debug(f"Wrapped type: {type_name}")
            return True
        return False
