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
    StructOrClass,
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
    def excludes(self):
        return self.context.excludes

    @property
    def excluded(self):
        return self.context.excluded

    @property
    def overloads(self):
        return self.context.overloads

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

    def create_builder(self, entry_key: str, cursor: cindex.Cursor = None) -> Node:
        return self.context.create_builder(entry_key, cursor)

    def lookup_node(self, key: str) -> Node:
        return self.context.lookup_node(key)
    
    def lookup_entry(self, key: str) -> Entry:
        return self.context.lookup_entry(key)
    

    def register_entry(self, entry: Entry):
        return self.context.register_entry(entry)

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

    def is_field_mappable(self, cursor):
        return self.is_cursor_mappable(cursor)

    def is_class_mappable(self, cursor):
        if not self.is_cursor_mappable(cursor):
            return False
        if not cursor.is_definition():
            return False
        return True

    def is_rvalue_ref(self, param):
        return param.kind == cindex.TypeKind.RVALUEREFERENCE

    def process_function_decl(self, decl):
        for param in decl.get_children():
            if param.kind == cindex.CursorKind.PARM_DECL:
                param_type = param.type
                if self.is_rvalue_ref(param_type):
                    logger.debug(f"Found rvalue reference in function {decl.spelling}")
                    return False
        return True

    def is_function_mappable(self, cursor):
        if not self.is_cursor_mappable(cursor):
            return False
        if "operator" in cursor.spelling:
            return False
        if not self.process_function_decl(cursor):
            return False
        for argument in cursor.get_arguments():
            if argument.type.get_canonical().kind == cindex.TypeKind.POINTER:
                ptr = argument.type.get_canonical().get_pointee().kind
                if ptr == cindex.TypeKind.FUNCTIONPROTO:
                    return False
            if argument.type.spelling == "va_list":
                return False
        return True

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

    def is_function_void_return(self, cursor):
        result = cursor.type.get_result()
        return result.kind == cindex.TypeKind.VOID

    def is_function_wrapped_return(self, cursor):
        result_type = cursor.result_type
        logger.debug(f"result_type: {result_type.spelling}")
        result_type_name = result_type.spelling.split(" ")[0]
        if result_type_name in self.wrapped:
            return True

    def is_field_readonly(self, cursor):
        if self.top_node.readonly:
            return True
        if cursor.type.is_const_qualified():
            return True
        if cursor.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        return False

    def is_overloaded(self, cursor) -> bool:
        return self.spell(cursor) in self.overloaded

    def should_wrap_function(self, cursor) -> bool:
        if cursor.type.is_function_variadic():
            return True

        result_type = cursor.result_type
        #logger.debug(f"result_type: {result_type.spelling}")
        result_type_name = result_type.spelling.split(" ")[0]
        if result_type_name in self.wrapped:
            return True

        for arg in cursor.get_arguments():
            if arg.type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True
            if self.should_return_argument(arg):
                return True

            #logger.debug(f"wrapped: {arg.spelling}: {self.arg_type(arg)}")
            #logger.debug(self.wrapped)

            type_name = arg.type.spelling.split(" ")[0]
            if type_name in self.wrapped:
                logger.debug(f"Found wrapped {arg.spelling}")
                return True
        return False

    def should_return_argument(self, argument) -> bool:
        argtype = argument.type.get_canonical()
        if argtype.kind == cindex.TypeKind.LVALUEREFERENCE:
            if not argtype.get_pointee().is_const_qualified():
                return True
        if argtype.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        if argtype.kind == cindex.TypeKind.POINTER:
            ptr = argtype.get_pointee()
            kinds = [
                cindex.TypeKind.BOOL,
                cindex.TypeKind.FLOAT,
                cindex.TypeKind.DOUBLE,
                cindex.TypeKind.INT,
                cindex.TypeKind.UINT,
                cindex.TypeKind.USHORT,
                cindex.TypeKind.ULONG,
                cindex.TypeKind.ULONGLONG,
            ]
            if not ptr.is_const_qualified() and ptr.kind in kinds:
                return True
        return False

    def get_function_result(self, node: Function, cursor) -> str:
        returned = [
            a.spelling for a in cursor.get_arguments() if self.should_return_argument(a)
        ]
        if not self.is_function_void_return(cursor) and not node.omit_ret:
            returned.insert(0, "ret")
        if len(returned) > 1:
            return "std::make_tuple({})".format(", ".join(returned))
        if len(returned) == 1:
            return returned[0]
        return ""

    def get_return_policy(self, cursor) -> str:
        result = cursor.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"

    def default_from_tokens(self, tokens) -> str:
        joined = "".join([t.spelling for t in tokens])
        parts = joined.split("=")
        if len(parts) == 2:
            return parts[1]
        return ""
    
    def write_pyargs(self, arguments, node: Function=None):
        for argument in arguments:
            default = self.default_from_tokens(argument.get_tokens())
            for child in argument.get_children():
                if child.type.kind in [cindex.TypeKind.POINTER]:
                    default = "nullptr"
                elif not len(default):
                    default = self.default_from_tokens(child.get_tokens())
            default = self.defaults.get(argument.spelling, default)
            if node and node.arguments and argument.spelling in node.arguments:
                node_argument = node.arguments[argument.spelling]
                #logger.debug(f"node_argument: {node_argument}")
                #exit()
                #default = node.arguments[argument.spelling].default
                default = str(node_argument['default'])
            # logger.debug(argument.spelling)
            # logger.debug(default)
            if len(default):
                default = " = " + default
            self(f', py::arg("{self.format_field(argument.spelling)}"){default}')

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
        '''
        if self.is_forward_declaration(cursor):
            return
        '''
        builder = self.create_builder(f'enum.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_field(self, cursor):
        '''
        if not self.is_field_mappable(cursor):
            return
        '''
        builder = self.create_builder(f'field.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

        self.top_node.add_child(node)

    # TODO: Handle is_deleted_method
    def visit_constructor(self, cursor):
        '''
        if not self.is_function_mappable(cursor):
            return
        '''
        builder = self.create_builder(f'ctor.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_function(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_method(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_function_or_method(self, cursor):
        '''
        if not self.is_function_mappable(cursor):
            return
        '''
        builder = self.create_builder(f'function.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_struct(self, cursor):
        '''
        if not self.is_class_mappable(cursor):
            return
        '''
        builder = self.create_builder(f'struct.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()

    def visit_class(self, cursor):
        '''
        if not self.is_class_mappable(cursor):
            return
        '''
        builder = self.create_builder(f'class.{self.spell(cursor)}', cursor=cursor)
        node = builder.build()


    def visit_var(self, cursor):
        #logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        pass

    def visit_using_decl(self, cursor):
        #logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        pass
