from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .builder_context import BuilderContext
from .node import Node, StructBaseNode


class Builder:
    actions: Dict[cindex.CursorKind, Callable] = {}

    def __init__(self, context: BuilderContext):
        super().__init__()
        self.context = context
        self.out = context.out

    @property
    def unit(self):
        return self.context.unit

    @property
    def prefixes(self) -> list[str]:
        return self.context.prefixes

    @property
    #def wrapped(self) -> dict[str, Node]:
    def wrapped(self) -> dict[str, StructBaseNode]:
        return self.context.wrapped

    '''
    @property
    def indent(self):
        return self.context.indentation
    '''

    @property
    def chaining(self) -> bool:
        return self.context.chaining
    
    @chaining.setter
    def chaining(self, value) -> None:
        self.context.chaining = value
    
    def begin_chain(self) -> None:
        self.context.chaining = True
        self.out(self.scope)

    def end_chain(self) -> None:
        self.context.chaining = False
        self.out(";")

    @property
    def text(self) -> str:
        #return self.context.text
        return self.out.text

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

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.context.push_node(node)
        self.out.indent()
        yield node
        self.out.dedent()
        self.context.pop_node()

    def push_node(self, node) -> None:
        self.context.push_node(node)

    def pop_node(self) -> Node:
        self.context.pop_node()

    @property
    def top_node(self) -> Optional[Node]:
        return self.context.top_node

    def spell(self, node: cindex.Cursor) -> str:
        return self.context.spell(node)

    def format_field(self, name: str) -> str:
        return self.context.format_field(name)

    def format_type(self, name: str) -> str:
        return self.context.format_type(name)

    def format_enum_constant(self, name: str, enum_name: str) -> str:
        return self.context.format_enum_constant(name, enum_name)

    def register_node(self, node: Node) -> str:
        return self.context.register_node(node)

    def lookup_node(self, key: str) -> Node:
        return self.context.lookup_node(key)

    def create_builder(self, entry_key: str, cursor: cindex.Cursor = None) -> Node:
        return self.context.create_builder(entry_key, cursor)

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

    def is_excluded(self, cursor: cindex.Cursor):
        if self.spell(cursor) in self.excluded:
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
        if cursor.location.file:
            node_path = Path(cursor.location.file.name)
            return node_path.name in self.mapped
        if cu.is_template(cursor):
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

    """
    def is_function_pointer(self, cursor):
        #if cursor.type.kind in [cindex.TypeKind.POINTER, cindex.TypeKind.TYPEDEF]:
        if cursor.type.kind in [cindex.TypeKind.POINTER, cindex.TypeKind.TYPEDEF]:
            ptr = cursor.type.get_canonical().get_pointee().kind
            if ptr == cindex.TypeKind.FUNCTIONPROTO:
                logger.debug(f'Function pointer: {ptr}: {cursor.spelling}')
                return True
        return False
    """

    def arg_type(self, argument: cindex.Cursor):
        if self.is_function_pointer(argument):
            logger.debug(f"Function pointer: {argument.spelling}")
            return argument.type.get_canonical().get_pointee().spelling

        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&"

        type_name = cu.get_base_type_name(argument.type)
        print(f"arg_type: {type_name}")

        if type_name in self.wrapped:
            wrapper = self.wrapped[type_name].wrapper
            return f"const {wrapper}&"
        
        #return argument.type.spelling
        return argument.type.get_canonical().spelling

    #TODO:  Might want to pass index to handle multiple unnamed arguments
    def arg_spelling(self, argument: cindex.Cursor):
        if argument.spelling == "":
            return "arg"
        return argument.spelling

    def arg_name(self, argument: cindex.Cursor):
        arg_spelling = self.arg_spelling(argument)
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{arg_spelling}[0]"
        return arg_spelling

    '''
    def arg_name(self, argument: cindex.Cursor):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{argument.spelling}[0]"
        return argument.spelling
    '''

    def arg_types(self, arguments: List[cindex.Cursor]):
        return ", ".join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments: List[cindex.Cursor]):
        return ', '.join([self.arg_name(a) for a in arguments])


    def arg_string(self, arguments: List[cindex.Cursor]):
        return ", ".join(
            ["{} {}".format(self.arg_type(a), self.arg_spelling(a)) for a in arguments]
        )

    '''
    def arg_string(self, arguments: List[cindex.Cursor]):
        return ", ".join(
            ["{} {}".format(self.arg_type(a), a.spelling) for a in arguments]
        )
    '''

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

    def visit(self, cursor: cindex.Cursor):
        # logger.debug(f"{cursor.kind} : {cursor.spelling}")
        if not self.is_cursor_mappable(cursor):
            return
        if not cursor.kind in self.actions:
            return
        self.actions[cursor.kind](self, cursor)

    def visit_children(self, cursor: cindex.Cursor):
        for child in cursor.get_children():
            self.visit(child)

    def visit_none(self, cursor: cindex.Cursor):
        logger.debug(f"visit_none: {cursor.spelling}")

    def visit_typedef_decl(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"typedef.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_enum(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"enum.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_field(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"field.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

        self.top_node.add_child(node)

    def visit_constructor(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"ctor.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_function(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"function.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_method(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"method.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_struct(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"struct.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_class(self, cursor: cindex.Cursor):
        builder = self.create_builder(f"class.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_var(self, cursor: cindex.Cursor):
        # logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        #pass
        raise NotImplementedError

    def visit_using_decl(self, cursor: cindex.Cursor):
        # logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        #pass
        raise NotImplementedError
