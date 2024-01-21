from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .context import GeneratorContext
from .entry import (
    Entry,
    FunctionEntry,
    CtorEntry,
    FieldEntry,
    MethodEntry,
    StructEntry,
    ClassEntry,
    EnumEntry,
    TypedefEntry,
)
from .node import (
    Node,
    FunctionNode,
    CtorNode,
    FieldNode,
    MethodNode,
    StructOrClassNode,
    StructNode,
    ClassNode,
    EnumNode,
    TypedefNode,
)
from .node_builder import (
    NodeBuilder,
    FunctionNodeBuilder,
    CtorNodeBuilder,
    FieldNodeBuilder,
    MethodNodeBuilder,
    StructNodeBuilder,
    ClassNodeBuilder,
    EnumNodeBuilder,
    TypedefNodeBuilder,
)

node_builder_cls_map = {
    "function": FunctionNodeBuilder,
    "ctor": CtorNodeBuilder,
    "field": FieldNodeBuilder,
    "method": MethodNodeBuilder,
    "struct": StructNodeBuilder,
    "class": ClassNodeBuilder,
    "enum": EnumNodeBuilder,
    "typedef": TypedefNodeBuilder,
}


class GeneratorBase(GeneratorContext):
    def __init__(self):
        super().__init__()
        self.indentation = 0
        self.text = ""
        self.source = ""
        self.mapped: List[str] = []  # headers we want to generate bindings for
        self.target = ""
        self.module = ""
        self.flags: List[str] = []
        self.defaults: Dict[str, str] = {}
        self.excludes: List[str] = []
        self.overloads: List[str] = []

        self.entries: Dict[str, Entry] = {}

        self.nodes: Dict[str, Node] = {}
        self.node_stack: List[Node] = []

    def __call__(self, line=""):
        if len(line):
            self.text += " " * self.indentation * 4
            self.text += line.replace(">>", "> >")
        self.text += "\n"

    @contextmanager
    def enter(self, node):
        self.push_node(node)
        self.indent()
        yield node
        self.dedent()
        self.pop_node()

    def __enter__(self):
        self.indent()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()

    def push_node(self, node):
        self.node_stack.append(node)

    def pop_node(self):
        self.node_stack.pop()

    def indent(self):
        self.indentation += 1

    def dedent(self):
        self.indentation -= 1

    @property
    def top_node(self):
        if len(self.node_stack) == 0:
            return None
        return self.node_stack[-1]

    def create_node(
        self, entry_key: str, cursor: cindex.Cursor = None, entry: Entry = None
    ) -> Node:
        kind, fqname = entry_key.split(".")
        builder_cls: NodeBuilder = node_builder_cls_map[kind]
        builder = builder_cls(self, fqname, cursor, entry)
        node = builder.build()
        self.nodes[fqname] = node

        return node

    def lookup_node(self, entry_key: str) -> Node:
        #logger.debug(f"Looking up {entry_key}")
        kind, key = entry_key.split(".")
        if key in self.nodes:
            return self.nodes[key]
        return None

    def lookup_entry(self, entry_key: str) -> Entry:
        #logger.debug(f"Looking up {entry_key}")
        kind, key = entry_key.split(".")
        if key in self.entries:
            return self.entries[key]
        return None

    def lookup_or_create_node(
        self, entry_key: str, cursor: cindex.Cursor = None
    ) -> Node:
        node = self.lookup_node(entry_key)
        if not node:
            entry = self.lookup_entry(entry_key)
            node = self.create_node(entry_key, cursor, entry)
        else:
            node.cursor = cursor
        return node

    def register_entry(self, entry: Entry):
        fqname = entry.name
        if entry.exclude:
            self.excludes.append(fqname)
        if entry.overload:
            self.overloads.append(fqname)
        if hasattr(entry, "gen_wrapper") and entry.gen_wrapper:
            logger.debug(f"Adding wrapped {fqname}")
            self.wrapped[fqname] = entry

        self.entries[fqname] = entry

        return entry

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
        # logger.debug(self.spell(cursor))
        # logger.debug(cursor.spelling)
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
                    print(f"Found rvalue reference in function {decl.spelling}")
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

    def get_function_result(self, node: FunctionNode, cursor) -> str:
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
    
    def write_pyargs(self, node: FunctionNode, arguments):
        for argument in arguments:
            default = self.default_from_tokens(argument.get_tokens())
            for child in argument.get_children():
                if child.type.kind in [cindex.TypeKind.POINTER]:
                    default = "nullptr"
                elif not len(default):
                    default = self.default_from_tokens(child.get_tokens())
            default = self.defaults.get(argument.spelling, default)
            if node.arguments and argument.spelling in node.arguments:
                node_argument = node.arguments[argument.spelling]
                #logger.debug(f"node_argument: {node_argument}")
                #exit()
                #default = node.arguments[argument.spelling].default
                default = str(node.arguments[argument.spelling]['default'])
            # logger.debug(argument.spelling)
            # logger.debug(default)
            if len(default):
                default = " = " + default
            self(f', py::arg("{self.format_field(argument.spelling)}"){default}')
