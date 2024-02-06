from typing import List, Dict, Tuple, Optional, Union, Any, Callable
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .builder_context import BuilderContext
from .node import (
    Node,
    FunctionNode,
    CtorNode,
    FieldNode,
    MethodNode,
    StructBaseNode,
    StructNode,
    ClassNode,
    EnumNode,
    TypedefNode,
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

    """
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
    """

    def register_node(self, node: Node):
        return self.context.register_node(node)

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

    """
    def resolve_type(self, type):
        # If the type is a typedef, resolve it to the actual type it refers to
        while type.kind == cindex.TypeKind.TYPEDEF:
            type = type.get_declaration().underlying_typedef_type
        return type
    """

    def resolve_type(self, type):
        # Resolve the type if it is a typedef or an alias, potentially recursively
        while type.kind == cindex.TypeKind.TYPEDEF:
            decl = type.get_declaration()
            if decl.kind in [
                cindex.CursorKind.TYPEDEF_DECL,
                cindex.CursorKind.TYPE_ALIAS_DECL,
                cindex.CursorKind.USING_DECLARATION,
                cindex.CursorKind.USING_DIRECTIVE,
            ]:
                type = decl.underlying_typedef_type
                # logger.debug(f"Resolving type: {type.kind} {type.spelling}")
            else:
                break
        return type

    def is_function_pointer(self, cursor):
        # logger.debug(f"Checking if {cursor.spelling} is a function pointer")
        # Resolve any typedef or alias and check if the type is a pointer to a function
        resolved_type = self.resolve_type(cursor.type)
        # logger.debug(f"Resolved type: {resolved_type.spelling}")
        return (
            resolved_type.kind == cindex.TypeKind.POINTER
            and resolved_type.get_pointee().kind == cindex.TypeKind.FUNCTIONPROTO
        )

    def arg_is_function_pointer(self, argument):
        name = argument.spelling
        result = self.is_function_pointer(argument)
        '''
        if name == "callback":
            logger.debug(f"Checking if {name} is a function pointer: {result}")
            logger.debug(
                f"kind: {argument.kind} type.kind: {argument.type.kind} {argument.type.spelling} {argument.type.get_canonical().kind} {argument.type.get_canonical().spelling}"
            )
            logger.debug(argument.type.get_pointee().kind)
            resolved_type = self.resolve_type(argument.type)
            logger.debug(f"Resolved type: {resolved_type.spelling}")
        '''
        return result

    """
    def is_function_pointer(self, cursor):
        type = self.resolve_type(cursor.type)
        if type.kind in [
            cindex.TypeKind.POINTER,
            cindex.TypeKind.TYPEDEF,
            cindex.CursorKind.TYPE_ALIAS_DECL,
            cindex.CursorKind.USING_DECLARATION,
            cindex.CursorKind.USING_DIRECTIVE,
        ]:
            ptr = cursor.type.get_canonical().get_pointee().kind
            if ptr == cindex.TypeKind.FUNCTIONPROTO:
                logger.debug(f"Function pointer: {ptr}: {cursor.spelling}")
                return True
        return False
    """

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

    def arg_type(self, argument):
        if self.is_function_pointer(argument):
            logger.debug(f"Function pointer: {argument.spelling}")
            # exit()
            return argument.type.get_canonical().get_pointee().spelling

        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&"

        type_name = argument.type.spelling.split(" ")[0]
        if type_name in self.wrapped:
            return argument.type.spelling.replace(
                type_name, self.wrapped[type_name].gen_wrapper["type"]
            )

        return argument.type.spelling

    def arg_name(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{argument.spelling}[0]"
        return argument.spelling

    def arg_types(self, arguments):
        return ", ".join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments: List[cindex.Cursor]):
        returned = []
        for a in arguments:
            type_name = a.type.spelling.split(" ")[0]
            if type_name in self.wrapped:
                returned.append(f"{self.arg_name(a)}->get()")
            else:
                returned.append(self.arg_name(a))
        return ", ".join(returned)

    """
    def arg_names(self, arguments):
        return ', '.join([self.arg_name(a) for a in arguments])
    """

    def arg_string(self, arguments):
        return ", ".join(
            ["{} {}".format(self.arg_type(a), a.spelling) for a in arguments]
        )

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
        # logger.debug(f"{cursor.kind} : {cursor.spelling}")
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
        builder = self.create_builder(f"typedef.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_enum(self, cursor):
        builder = self.create_builder(f"enum.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_field(self, cursor):
        builder = self.create_builder(f"field.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

        self.top_node.add_child(node)

    # TODO: Handle is_deleted_method
    def visit_constructor(self, cursor):
        builder = self.create_builder(f"ctor.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_function(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_method(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_function_or_method(self, cursor):
        builder = self.create_builder(f"function.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_struct(self, cursor):
        builder = self.create_builder(f"struct.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_class(self, cursor):
        builder = self.create_builder(f"class.{self.spell(cursor)}", cursor=cursor)
        node = builder.build()

    def visit_var(self, cursor):
        # logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        pass

    def visit_using_decl(self, cursor):
        # logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        pass
