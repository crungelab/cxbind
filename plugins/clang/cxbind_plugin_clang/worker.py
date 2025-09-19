from typing import TypeVar, Generic, List, Dict, Tuple, Optional, Union, Any, Callable, Generator
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .worker_context import WorkerContext
from .node import Node, StructBaseNode

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
    def wrapped(self) -> dict[str, StructBaseNode]:
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
            return node.spec.pyname or node.pyname

    def module_(self, node: Node):
        if node.kind == "root":
            return self.module
        else:
            return node.spec.pyname or node.pyname

    '''
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
    '''

    '''
    @property
    def scope(self) -> str:
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
    '''

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

    def is_cursor_mappable(self, cursor: cindex.Cursor):
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
                # logger.debug(f"Not mappable: {node_path.name}")
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

    def arg_type(self, argument: cindex.Cursor):
        arg_kind = argument.kind
        # logger.debug(f"arg_kind: {arg_kind}")
        arg_type = argument.type
        # logger.debug(arg_type.spelling)
        arg_type_kind = arg_type.kind
        # logger.debug(arg_type_kind)
        if self.is_function_pointer(argument):
            logger.debug(f"Function pointer: {argument.spelling}")
            return argument.type.get_canonical().get_pointee().spelling

        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            logger.debug(f"Constant array: {argument.spelling}")
            element_type = argument.type.get_array_element_type()
            # element_type_name = argument.type.get_array_element_type().spelling
            element_type_name = cu.get_base_type_name(
                argument.type.get_array_element_type()
            )  # Strip qualifiers
            logger.debug(f"Element type: {element_type.spelling}")
            logger.debug(f"Element type kind: {element_type.kind}")
            if element_type.kind == cindex.TypeKind.UNEXPOSED:
                resolved_type = element_type.get_canonical()
                specialization_node = self.top_node
                resolved_type_name = self.resolve_template_type(
                    resolved_type.spelling, specialization_node.spec.args
                )
                logger.debug(f"Resolved type: {resolved_type_name}")
                element_type_name = resolved_type_name

            # return f"std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&"
            return f"std::array<{element_type_name}, {argument.type.get_array_size()}>&"

        # Handle template parameters (placeholders)
        if arg_type_kind == cindex.TypeKind.UNEXPOSED:
            specialization_node = self.top_node
            logger.debug(f"specialization_node: {specialization_node}")
            logger.debug(f"specialization_node.spec: {specialization_node.spec}")
            # Attempt to get the canonical type spelling for the template argument
            resolved_type = argument.type.get_canonical()
            resolved_type_name = self.resolve_template_type(
                resolved_type.spelling, specialization_node.spec.args
            )
            logger.debug(f"Resolved template parameter: {resolved_type}")
            logger.debug(f"Resolved template parameter: {resolved_type_name}")
            type_name = cu.get_base_type_name(argument.type)
            logger.debug(f"arg_type: {type_name}")
            return resolved_type_name
            # return type_name

        type_name = cu.get_base_type_name(argument.type)
        # logger.debug(f"arg_type: {type_name}")

        if type_name in self.wrapped:
            wrapper = self.wrapped[type_name].wrapper
            return f"const {wrapper}&"

        return argument.type.get_canonical().spelling

    def resolve_template_type(self, template_param, template_mapping):
        """
        Resolve a template parameter to its actual specialized type using the mapping.
        """
        # Detect if the parameter is in the form of `type-parameter-X-Y`
        if "type-parameter" in template_param:
            index = int(
                template_param.split("-")[-1]
            )  # Extract the index (e.g., `0` from `type-parameter-0-0`)
            # Use the index to fetch the corresponding argument from the template mapping
            if index < len(template_mapping):
                return template_mapping[index]
        # Otherwise, just return the parameter as-is
        return template_param

    # TODO:  Might want to pass index to handle multiple unnamed arguments
    def arg_spelling(self, argument: cindex.Cursor):
        if argument.spelling == "":
            return "arg"
        return argument.spelling

    def arg_name(self, argument: cindex.Cursor):
        arg_spelling = self.arg_spelling(argument)
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{arg_spelling}[0]"
        return arg_spelling

    def arg_types(self, arguments: List[cindex.Cursor]):
        return ", ".join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments: List[cindex.Cursor]):
        return ", ".join([self.arg_name(a) for a in arguments])

    def arg_string(self, arguments: List[cindex.Cursor]):
        result = []
        for a in arguments:
            arg_type = self.arg_type(a)
            arg_spelling = self.arg_spelling(a)

            if arg_type.endswith("[]"):
                # Remove the array brackets for the argument type
                arg_type = arg_type[:-2]
                # Add the array brackets to the argument spelling
                arg_spelling = f"{arg_spelling}[]"

            result.append(f"{arg_type} {arg_spelling}")
        return ", ".join(result)

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

