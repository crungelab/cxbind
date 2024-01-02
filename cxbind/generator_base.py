import re
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from . import cu
from .entry import EntryContext, Entry, FunctionEntry, CtorEntry, FieldEntry, MethodEntry, StructEntry, ClassEntry, EnumEntry, TypedefEntry

entry_cls_map = {
    'function': FunctionEntry,
    'ctor': CtorEntry,
    'field': FieldEntry,
    'method': MethodEntry,
    'struct': StructEntry,
    'class': ClassEntry,
    'enum': EnumEntry,
    'typedef': TypedefEntry,
}

class GeneratorBase(EntryContext):
    def __init__(self):
        super().__init__()
        self.indentation = 0
        self.text = ''
        self.source = ''
        self.mapped = [] #headers we want to generate bindings for
        self.target = ''
        self._prefix = ''
        self._short_prefix = ''
        self.module = ''
        self.flags = []
        self.defaults = {}
        self.excludes = []
        self.overloads = []

        self.entries = {}
        self.entry_stack = []

    def __call__(self, line=""):
        if len(line):
            self.text += ' ' * self.indentation * 4
            self.text += line.replace('>>', '> >')
        self.text += '\n'

    @contextmanager
    def enter(self, entry):
        self.push_entry(entry)
        self.indent()
        yield entry
        self.dedent()
        self.pop_entry()

    def __enter__(self):
        self.indent()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()

    def push_entry(self, entry):
        self.entry_stack.append(entry)

    def pop_entry(self):
        self.entry_stack.pop()

    def indent(self):
        self.indentation +=1

    def dedent(self):
        self.indentation -=1

    @property
    def entry(self):
        if len(self.entry_stack) == 0:
            return None
        return self.entry_stack [-1]

    def lookup(self, entry_key: str):
        print(entry_key)
        kind, key = entry_key.split('.')
        if key in self.entries:
            return self.entries[key]
        return None

    def lookup_or_create(self, entry_key: str, config: dict = {}, node: cindex.Cursor = None):
        entry = self.lookup(entry_key)
        if not entry:
            entry = self.create_entry(entry_key, config, node)
        else:
            entry.node = node
        return entry

    def create_entry(self, entry_key: str, config: dict = {}, node: cindex.Cursor = None):
        kind, fqname = entry_key.split('.')
        cls = entry_cls_map[kind]
        #TODO: make produce class method?
        entry = cls(self, fqname, config, node)

        if entry.exclude:
            self.excludes.append(fqname)
        if entry.overload:
            self.overloads.append(fqname)

        self.entries[fqname] = entry

        return entry

    @property
    def scope(self):
        entry = self.entry
        if entry is None:
            return self.module
        else:
            return entry.pyname

    def module_(self, entry: Entry):
        if entry is None:
            return self.module
        else:
            return entry.pyname

    def is_excluded(self, node):
        #logger.debug(self.spell(node))
        #logger.debug(node.spelling)
        if self.spell(node) in self.excluded:
            return True
        if node.spelling.startswith('_'):
            return True
        return False

    def is_node_mappable(self, node):
        if self.is_excluded(node):
            return False
        if node.access_specifier == cindex.AccessSpecifier.PRIVATE:
            return False
        if node.access_specifier == cindex.AccessSpecifier.PROTECTED:
            return False
        #print(node.location.file.name)
        if node.location.file:
            node_path = Path(node.location.file.name)
            return node_path.name in self.mapped
        if cu.is_template(node):
            return False
        return True

    def is_field_mappable(self, node):
        return self.is_node_mappable(node)

    def is_class_mappable(self, node):
        if not self.is_node_mappable(node):
            return False
        if not node.is_definition():
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

    def is_function_mappable(self, node):
        if not self.is_node_mappable(node):
            return False
        if 'operator' in node.spelling:
            return False
        if not self.process_function_decl(node):
            return False
        for argument in node.get_arguments():
            if argument.type.get_canonical().kind == cindex.TypeKind.POINTER:
                ptr = argument.type.get_canonical().get_pointee().kind
                if ptr == cindex.TypeKind.FUNCTIONPROTO:
                    return False
            if argument.type.spelling == 'va_list':
                return False
        return True

    def is_char_ptr(self, node):
        if node.type.get_canonical().kind == cindex.TypeKind.POINTER:
            ptr = node.type.get_canonical().get_pointee().kind
            #logger.debug(f'{ptr}: {node.spelling}')
            if ptr == cindex.TypeKind.CHAR_S:
                return True
        return False

    def is_fn_ptr(self, node):
        if node.type.kind in [cindex.TypeKind.POINTER, cindex.TypeKind.TYPEDEF]:
            ptr = node.type.get_canonical().get_pointee().kind
            #logger.debug(f'{ptr}: {node.spelling}')
            if ptr == cindex.TypeKind.FUNCTIONPROTO:
                return True
        return False

    def is_forward_declaration(self, node):
        definition = node.get_definition()

        # If the definition is null, then there is no definition in this translation
        # unit, so this cursor must be a forward declaration.
        if not definition:
            return True
        # If there is a definition, then the forward declaration and the definition
        # are in the same translation unit. This cursor is the forward declaration if
        # it is _not_ the definition.
        return node != definition

    def is_function_void_return(self, node):
        result = node.type.get_result()
        return result.kind == cindex.TypeKind.VOID

    def is_field_readonly(self, node):
        if self.entry.readonly:
            return True
        if node.type.is_const_qualified():
            return True
        if node.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return True
        return False

    def is_overloaded(self, node):
        return self.spell(node) in self.overloaded

    def should_wrap_function(self, node):
        if node.type.is_function_variadic():
            return True
        for arg in node.get_arguments():
            if arg.type.kind == cindex.TypeKind.CONSTANTARRAY:
                return True
            if self.should_return_argument(arg):
                return True
        return False

    def should_return_argument(self, argument):
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

    def arg_type(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f'std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&'
        return argument.type.spelling

    def arg_name(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f'&{argument.spelling}[0]'
        return argument.spelling

    def arg_types(self, arguments):
        return ', '.join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments):
        return ', '.join([self.arg_name(a) for a in arguments])

    def arg_string(self, arguments):
        return ', '.join(['{} {}'.format(self.arg_type(a), a.spelling) for a in arguments])

    def default_from_tokens(self, tokens):
        joined = ''.join([t.spelling for t in tokens])
        parts = joined.split('=')
        if len(parts) == 2:
            return parts[1]
        return ''

    def get_function_return(self, node):
        returned = [
            a.spelling for a in node.get_arguments() if self.should_return_argument(a)
        ]
        if not self.is_function_void_return(node):
            returned.insert(0, "ret")
        if len(returned) > 1:
            return "std::make_tuple({})".format(", ".join(returned))
        if len(returned) == 1:
            return returned[0]
        return ""

    def get_return_policy(self, node):
        result = node.type.get_result()
        if result.kind == cindex.TypeKind.LVALUEREFERENCE:
            return "py::return_value_policy::reference"
        else:
            return "py::return_value_policy::automatic_reference"


    def write_pyargs(self, arguments):
        for argument in arguments:
            default = self.default_from_tokens(argument.get_tokens())
            for child in argument.get_children():
                if child.type.kind in [cindex.TypeKind.POINTER]:
                    default = 'nullptr'
                elif not len(default):
                    default = self.default_from_tokens(child.get_tokens())
            default = self.defaults.get(argument.spelling, default)
            #logger.debug(argument.spelling)
            #logger.debug(default)
            if len(default):
                default = ' = ' + default
            self(f', py::arg("{self.format_field(argument.spelling)}"){default}')
