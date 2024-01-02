import os
from pathlib import Path
import importlib
from loguru import logger
import jinja2

from clang import cindex

from .generator_base import GeneratorBase
from .yaml import load_yaml

from . import cu
from . import UserSet
from .entry import EntryContext, Entry, FunctionEntry, CtorEntry, FieldEntry, MethodEntry, StructOrClassEntry, StructEntry, ClassEntry, EnumEntry, TypedefEntry

class Options:
    def __init__(self, *options, **kwargs):
        for dictionary in options:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

class Overloaded(UserSet):
    def __init__(self, data) -> None:
        super().__init__(data)
        self.visited = set()

    def is_overloaded(self, node):
        return self.name(node) in self

class Generator(GeneratorBase):
    def __init__(self, config, **kwargs):
        super().__init__()
        self.excludes = []
        self.overloads = []
        self.config = config
        self.options = { 'save': True }
        for key, value in config.items():
            #logger.debug(config[key])
            if '.' in key:
                self.create_entry(key, value)
            else:
                setattr(self, key, value)

        for key in kwargs:
            if key == 'options':
                options = kwargs[key]
                options.update(self.options)
                self.options = options

            setattr(self, key, kwargs[key])
        
        self.options = Options(self.options)
        self.excluded = set(self.excludes)
        self.overloaded = Overloaded(self.overloads)

        BASE_PATH = Path('.')
        self.path = BASE_PATH / self.source
        self.mapped.append(self.path.name)

    @classmethod
    def create(self, name="cxbind"):
        filename = f'{name}.yaml'
        print(f'processing:  {filename}')
        path = Path(os.getcwd(), '.cxbind', filename)
        #logger.debug(path)
        config = load_yaml(path)
        config['name'] = name
        instance = Generator(config)
        instance.import_actions()
        return instance

    def import_actions(self):
        path = Path(os.path.dirname(os.path.abspath(__file__)), 'actions.py')
        spec = importlib.util.spec_from_file_location(
            "actions", path
        )
        __actions__ = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(__actions__)

        self.actions = __actions__.MAP

    def generate(self):
        #logger.debug(self.path)
        #tu = cindex.Index.create().parse(self.path, args=self.flags)
        tu = cindex.TranslationUnit.from_source(self.path, args=self.flags, options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

        with self:
            self.visit_overloads(tu.cursor)
            self.visit_children(tu.cursor)

        #Jinja
        config = self.config
        #logger.debug(self.config)
        config['body'] = self.text
        self.searchpath = Path('.')  / '.cxbind'
        loader = jinja2.FileSystemLoader(searchpath=self.searchpath)
        env = jinja2.Environment(loader=loader)

        template = env.get_template(f'{self.name}.cpp')
        rendered = template.render(config)
        filename = self.target
        with open(filename,'w') as fh:
            fh.write(rendered)

    def visit_none(self, node):
        logger.debug(f"visit_none: {node.spelling}")

    '''
    def visit_enum(self, node):
        if self.is_forward_declaration(node):
            return
        if node.is_scoped_enum():
            return self.visit_scoped_enum(node)
        self(
            f'py::enum_<{self.spell(node)}>({self.module}, "{self.format_type(node.spelling)}", py::arithmetic())'
        )
        with self:
            for child in node.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {child.spelling})'
                )
            self(".export_values();")
        self()
    '''
    def visit_typedef_decl(self, node):
        logger.debug(node.spelling)
        #if not self.is_typedef_mappable(node):
        #    return
        entry: Entry = self.lookup_or_create(f'typedef.{self.spell(node)}', node=node)
        logger.debug(entry)
        self.push_entry(entry)
        self.visit_children(node)
        self.pop_entry()

    def visit_enum(self, node):
        logger.debug(node.spelling)
        if self.is_forward_declaration(node):
            return
        if node.is_scoped_enum():
            return self.visit_scoped_enum(node)
        
        typedef_parent = self.entry if isinstance(self.entry, TypedefEntry) else None

        if typedef_parent:
            fqname = typedef_parent.fqname
            pyname = typedef_parent.pyname
        else:
            fqname = self.spell(node)
            pyname = self.format_type(node.spelling)

        #TODO: for some reason it's visiting the same enum twice when typedef'd
        if not pyname:
            return
        
        self(
            f'py::enum_<{fqname}>({self.module}, "{pyname}", py::arithmetic())'
        )
        with self:
            for child in node.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self()

    def visit_struct_enum(self, node):
        entry = self.entry
        if not node.get_children():
            return
        self(
            f'py::enum_<{self.spell(node)}>({self.module}, "{entry.pyname}", py::arithmetic())'
        )
        logger.debug(node.spelling)
        with self:
            for child in node.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {entry.fqname}::Enum::{child.spelling})'
                )
            self(".export_values();")
        self("")

    def visit_scoped_enum(self, node):
        logger.debug(node.spelling)
        fqname = self.spell(node)
        # logger.debug(fqname)
        pyname = self.format_type(node.spelling)
        self(f"PYENUM_SCOPED_BEGIN({self.module}, {fqname}, {pyname})")
        self(pyname)
        with self:
            for child in node.get_children():
                #logger.debug(child.kind) #CursorKind.ENUM_CONSTANT_DECL
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self(f"PYENUM_SCOPED_END({self.module}, {fqname}, {pyname})\n")
        self()

    # TODO: Handle is_deleted_method
    def visit_constructor(self, node):
        if not self.is_function_mappable(node):
            return
        #TODO: This should be in Clang 15.06, but it's not ...
        #if node.is_deleted_method():
        #    return
        if self.entry.readonly:
            return
        self.entry.has_constructor = True
        arguments = [a for a in node.get_arguments()]
        if len(arguments):
            self(
                f"{self.scope}.def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            self(");")
        else:
            self(f"{self.scope}.def(py::init<>());")


    def visit_field(self, node):
        if not self.is_field_mappable(node):
            return
        entry: FieldEntry = self.lookup_or_create(f'field.{self.spell(node)}', node=node)
        self.entry.add_child(entry)
        #logger.debug(entry)

        '''
        self.print_type_info(node)
        if node.spelling == 'disposeCallback':
            breakpoint()
        '''

        logger.debug(f'{node.type.spelling}, {node.type.kind}: {node.displayname}')
        
        if self.is_field_readonly(node):
            self(f'{self.scope}.def_readonly("{entry.pyname}", &{entry.fqname});')
        else:
            if self.is_char_ptr(node):
                #logger.debug(f"{node.spelling}: is char*")
                self.visit_char_ptr_field(node, entry.pyname)
            elif self.is_fn_ptr(node):
                #logger.debug(f"{node.spelling}: is fn*")
                self.visit_fn_ptr_field(node, entry.pyname)
            else:
                self(f'{self.scope}.def_readwrite("{entry.pyname}", &{entry.fqname});')

    #TODO: I am sure this is creating memory leaks
    def visit_char_ptr_field(self, node, pyname):
        pname = self.spell(node.semantic_parent)
        name = node.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[](const {pname}& self)' '{'
            f' return self.{name};'
            ' },'
            f'[]({pname}& self, std::string source)' '{'
            ' char* c = (char *)malloc(source.size());'
            ' strcpy(c, source.c_str());'
            f' self.{name} = c;'
            ' }'
            )
        self(');')

    def visit_fn_ptr_field(self, node, pyname):
        pname = self.spell(node.semantic_parent)
        name = node.spelling
        typename = node.type.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[]({pname}& self)' '{'
            f' return self.{name};'
            ' },'
            f'[]({pname}& self, {typename} source)' '{'
            f' self.{name} = source;'
            ' }'
            )
        self(');')

    def visit_function(self, node):
        self.visit_function_or_method(node)

    def visit_method(self, node):
        self.visit_function_or_method(node)

    def visit_function_or_method(self, node):
        #logger.debug(node.spelling)
        if not self.is_function_mappable(node):
            return
        mname = self.scope
        arguments = [a for a in node.get_arguments()]
        cname = "&" + self.spell(node)
        pyname = self.format_field(node.spelling)
        if self.is_overloaded(node):
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname})"
        if self.should_wrap_function(node):
            self(f'{mname}.def("{pyname}", []({self.arg_string(arguments)})')
            self("{")
            ret = "" if self.is_function_void_return(node) else "auto ret = "
            with self:
                self(f"{ret}{self.spell(node)}({self.arg_names(arguments)});")
                self(f"return {self.get_function_return(node)};")
            self("}")
        else:
            self(f'{mname}.def("{pyname}", {cname}')
        self.write_pyargs(arguments)
        self(f", {self.get_return_policy(node)});\n")

    def visit_struct(self, node):
        if not self.is_class_mappable(node):
            return
        entry: StructEntry = self.lookup_or_create(f'struct.{self.spell(node)}', node=node)
        fqname = entry.fqname
        pyname = entry.pyname
        if not pyname:
            return

        #logger.debug(entry)
        children = list(node.get_children())  # it's an iterator
        wrapped = False
        # Handle the case of a struct with one enum child
        if len(children) == 1:
            first_child = children[0]
            wrapped = first_child.kind == cindex.CursorKind.ENUM_DECL
        if not wrapped:
            base = None
            for child in node.get_children():
                if child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                    base = child
            if base:
                basename = self.spell(base)
                self(f"PYSUBCLASS_BEGIN({self.module}, {fqname}, {basename}, {pyname})")
            else:
                self(f"PYCLASS_BEGIN({self.module}, {fqname}, {pyname})")
        with self.enter(entry):
            #TODO: this is a can of worms trying to map substructures.  Might be worth it if I can figure it out.
            # May add a flag to the yaml to indicate whether to map substructures or not.  example: traverse: shallow|deep
            self.visit_children(node)
            '''
            for child in node.get_children():
                # logger.debug(f"{child.kind} : {child.spelling}")
                if child.kind == cindex.CursorKind.CONSTRUCTOR:
                    self.visit_constructor(child)
                elif child.kind == cindex.CursorKind.CXX_METHOD:
                    self.visit_function(child)
                elif child.kind == cindex.CursorKind.FIELD_DECL:
                    self.visit_field(child)
                elif child.kind == cindex.CursorKind.ENUM_DECL:
                    self.visit_struct_enum(child)
                elif child.kind == cindex.CursorKind.USING_DECLARATION:
                    self.visit_using_decl(child)
            '''
            if entry.gen_init:
                self.gen_init()
            elif entry.gen_kw_init:
                self.gen_kw_init()

        if not wrapped:
            self(f"PYCLASS_END({self.module}, {fqname}, {pyname})\n")

    def visit_class(self, node):
        if not self.is_class_mappable(node):
            return
        entry: ClassEntry = self.lookup_or_create(f'class.{self.spell(node)}', node=node)
        #logger.debug(entry)
        self(f"PYCLASS_BEGIN({self.module}, {entry.fqname}, {entry.pyname})")
        with self.enter(entry):
            self.visit_children(node)

            if entry.gen_init:
                self.gen_init()
            elif entry.gen_kw_init:
                self.gen_kw_init()

        self(f"PYCLASS_END({self.module}, {entry.fqname}, {entry.pyname})\n")

    def gen_init(self):
        self(f"{self.scope}.def(py::init<>());")

    def gen_kw_init(self):
        entry = self.entry
        self(f'{self.scope}.def(py::init([](const py::kwargs& kwargs)')
        self("{")
        with self:
            self(f'{entry.fqname} obj;')
            for child in entry.children:
                node = child.node
                typename = None
                is_char_ptr = self.is_char_ptr(node)
                if is_char_ptr:
                    typename = 'std::string'
                else:
                    typename = node.type.spelling
                if type(child) is FieldEntry:
                    self(f'if (kwargs.contains("{child.pyname}"))')
                    self("{")
                    with self:
                        if is_char_ptr:
                            self(f'auto _value = kwargs["{child.pyname}"].cast<{typename}>();')
                            self(f'char* value = (char*)malloc(_value.size());')
                            self(f'strcpy(value, _value.c_str());')
                        else:
                            self(f'auto value = kwargs["{child.pyname}"].cast<{typename}>();')
                        self(f'obj.{child.name} = value;')
                    self("}")
            self('return obj;')
        self("}), py::return_value_policy::automatic_reference);")


    def visit_var(self, node):
        #logger.debug(f"Not implemented:  visit_var: {node.spelling}")
        pass

    def visit_using_decl(self, node):
        #logger.debug(f"Not implemented:  visit_using_decl: {node.spelling}")
        pass

    def visit(self, node):
        self.actions[node.kind](self, node)

    def visit_children(self, node):
        for child in node.get_children():
            if not self.is_node_mappable(child):
                continue
            # logger.debug(child.spelling, ':  ', child.kind)
            kind = child.kind
            if kind in self.actions:
                self.visit(child)

    def visit_overloads(self, node):
        for child in node.get_children():
            if child.kind in [
                cindex.CursorKind.CXX_METHOD,
                cindex.CursorKind.FUNCTION_DECL,
            ]:
                key = self.spell(child)
                if key in self.overloaded.visited:
                    self.overloaded.add(key)
                else:
                    self.overloaded.visited.add(key)
            elif self.is_node_mappable(child):
                self.visit_overloads(child)
