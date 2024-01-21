import os
from pathlib import Path
import importlib
from loguru import logger
import jinja2

from clang import cindex

from .yaml import load_yaml

from . import cu
from . import UserSet

from .node import Node, FunctionNode, CtorNode, FieldNode, MethodNode, StructOrClassNode, StructNode, ClassNode, EnumNode, TypedefNode

#from .generator_base import GeneratorBase
from .generator_config import GeneratorConfig
from .builder import Builder
from .builder_context import BuilderContext

#TODO: Use pydantic settings
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

    def is_overloaded(self, cursor):
        return self.name(cursor) in self

class Generator(Builder):
    def __init__(self, name: str, config: GeneratorConfig, **kwargs):
        super().__init__(BuilderContext())
        logger.debug(f"Generator: {name}")
        self.name = name
        self.config = config
        #self.excludes = []
        #self.overloads = []
        self.options = { 'save': True }

        #self.__dict__.update(config.model_dump())
        '''
        for attr in vars(config):
            setattr(self, attr, getattr(config, attr))
        '''
        for attr in vars(config):
            setattr(self.context, attr, getattr(config, attr))

        '''
        self.source = config.source
        self.target = config.target
        self.flags = config.flags
        self.module = config.module
        '''

        for entry in config.function:
            self.register_entry(entry)
        for entry in config.method:
            self.register_entry(entry)
        for entry in config.struct:
            self.register_entry(entry)
        for entry in config.cls:
            self.register_entry(entry)
        for entry in config.field:
            self.register_entry(entry)

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

        config_searchpath = BASE_PATH  / '.cxbind' / 'templates'
        default_searchpath = Path(os.path.dirname(os.path.abspath(__file__)), 'templates')
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

    @classmethod
    def create(self, name="cxbind"):
        filename = f'{name}.yaml'
        print(f'processing:  {filename}')
        path = Path(os.getcwd(), '.cxbind', filename)
        #logger.debug(path)
        yaml_data = load_yaml(path)

        logger.debug(f"yaml_data: {yaml_data}")

        # Process the entries
        data = {}
        for key, value in yaml_data.items():
            if '.' in key:
                entry_kind, entry_fqname = key.split('.')
                value['fqname'] = entry_fqname
                value['kind'] = entry_kind
                if entry_kind in data:
                    data[entry_kind].append(value)
                else:
                    data[entry_kind] = [value]
            else:
                data[key] = value

        logger.debug(f"processed_data: {data}")

        # Validate with Pydantic
        config = GeneratorConfig.model_validate(data)

        logger.debug(f"config: {config}")

        # Dump the Pydantic model
        logger.debug(f"config.json(): {config.model_dump_json()}")

        instance = Generator(name, config)
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
        tu = cindex.TranslationUnit.from_source(self.path, args=self.flags, options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

        with self:
            self.visit_overloads(tu.cursor)
            self.visit_children(tu.cursor)

        #Jinja
        context = {
            'body': self.text
        }

        template = self.jinja_env.get_template(f'{self.name}.cpp')
        rendered = template.render(context)
        filename = self.target
        with open(filename,'w') as fh:
            fh.write(rendered)

    def visit_none(self, cursor):
        logger.debug(f"visit_none: {cursor.spelling}")

    def visit_typedef_decl(self, cursor):
        logger.debug(cursor.spelling)
        node: Node = self.lookup_or_create_node(f'typedef.{self.spell(cursor)}', cursor=cursor)
        logger.debug(node)
        self.push_node(node)
        self.visit_children(cursor)
        self.pop_node()

    def visit_enum(self, cursor):
        logger.debug(cursor.spelling)
        if self.is_forward_declaration(cursor):
            return
        if cursor.is_scoped_enum():
            return self.visit_scoped_enum(cursor)
        
        typedef_parent = self.top_node if isinstance(self.top_node, TypedefNode) else None

        if typedef_parent:
            fqname = typedef_parent.fqname
            pyname = typedef_parent.pyname
        else:
            fqname = self.spell(cursor)
            pyname = self.format_type(cursor.spelling)

        #TODO: for some reason it's visiting the same enum twice when typedef'd
        if not pyname:
            return
        
        self(
            f'py::enum_<{fqname}>({self.module}, "{pyname}", py::arithmetic())'
        )
        with self:
            for child in cursor.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self()

    def visit_struct_enum(self, cursor):
        node = self.top_node
        if not cursor.get_children():
            return
        self(
            f'py::enum_<{self.spell(cursor)}>({self.module}, "{node.pyname}", py::arithmetic())'
        )
        logger.debug(cursor.spelling)
        with self:
            for child in cursor.get_children():
                self(
                    f'.value("{self.format_enum(child.spelling)}", {node.fqname}::Enum::{child.spelling})'
                )
            self(".export_values();")
        self()

    def visit_scoped_enum(self, cursor):
        logger.debug(cursor.spelling)
        fqname = self.spell(cursor)
        # logger.debug(fqname)
        pyname = self.format_type(cursor.spelling)
        self(f"PYENUM_SCOPED_BEGIN({self.module}, {fqname}, {pyname})")
        self(pyname)
        with self:
            for child in cursor.get_children():
                #logger.debug(child.kind) #CursorKind.ENUM_CONSTANT_DECL
                self(
                    f'.value("{self.format_enum(child.spelling)}", {fqname}::{child.spelling})'
                )
            self(".export_values();")
        self(f"PYENUM_SCOPED_END({self.module}, {fqname}, {pyname})")
        self()

    # TODO: Handle is_deleted_method
    def visit_constructor(self, cursor):
        if not self.is_function_mappable(cursor):
            return
        #TODO: This should be in Clang 15.06, but it's not ...
        #if cursor.is_deleted_method():
        #    return
        if self.top_node.readonly:
            return
        self.top_node.has_constructor = True
        arguments = [a for a in cursor.get_arguments()]
        if len(arguments):
            self(
                f"{self.scope}.def(py::init<{self.arg_types(arguments)}>()"
            )
            self.write_pyargs(arguments)
            self(");")
        else:
            self(f"{self.scope}.def(py::init<>());")


    def visit_field(self, cursor):
        if not self.is_field_mappable(cursor):
            return
        node: FieldNode = self.lookup_or_create_node(f'field.{self.spell(cursor)}', cursor=cursor)
        self.top_node.add_child(node)
        #logger.debug(node)

        logger.debug(f'{cursor.type.spelling}, {cursor.type.kind}: {cursor.displayname}')
        
        if self.is_field_readonly(cursor):
            self(f'{self.scope}.def_readonly("{node.pyname}", &{node.fqname});')
        else:
            if self.is_char_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is char*")
                self.visit_char_ptr_field(cursor, node.pyname)
            elif self.is_fn_ptr(cursor):
                #logger.debug(f"{cursor.spelling}: is fn*")
                self.visit_fn_ptr_field(cursor, node.pyname)
            else:
                self(f'{self.scope}.def_readwrite("{node.pyname}", &{node.fqname});')

    #TODO: This is creating memory leaks.  Need wrapper functionality pronto.
    def visit_char_ptr_field(self, cursor, pyname):
        pname = self.spell(cursor.semantic_parent)
        name = cursor.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[](const {pname}& self)' '{'
            f' return self.{name};'
            ' },'
            )
            self(
            f'[]({pname}& self, std::string source)' '{'
            ' char* c = (char *)malloc(source.size() + 1);'
            ' strcpy(c, source.c_str());'
            f' self.{name} = c;'
            ' }'
            )
        self(');')

    def visit_fn_ptr_field(self, cursor, pyname):
        pname = self.spell(cursor.semantic_parent)
        name = cursor.spelling
        typename = cursor.type.spelling
        self(f'{self.scope}.def_property("{pyname}",')
        with self:
            self(
            f'[]({pname}& self)' '{'
            f' return self.{name};'
            ' },')
            self(
            f'[]({pname}& self, {typename} source)' '{'
            f' self.{name} = source;'
            ' }'
            )
        self(');')

    def visit_function(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_method(self, cursor):
        self.visit_function_or_method(cursor)

    def visit_function_or_method(self, cursor):
        #logger.debug(cursor.spelling)
        if not self.is_function_mappable(cursor):
            return
        node: FunctionNode = self.lookup_or_create_node(f'function.{self.spell(cursor)}', cursor=cursor)
        mname = self.scope
        arguments = [a for a in cursor.get_arguments()]
        cname = "&" + self.spell(cursor)
        pyname = self.format_field(cursor.spelling)
        if self.is_overloaded(cursor):
            cname = f"py::overload_cast<{self.arg_types(arguments)}>({cname})"
        if self.should_wrap_function(cursor):
            self(f'{mname}.def("{pyname}", []({self.arg_string(arguments)})')
            self("{")
            ret = "" if self.is_function_void_return(cursor) else "auto ret = "

            result = f"{self.spell(cursor)}({self.arg_names(arguments)})"
            result_type = cursor.result_type
            #logger.debug(f'result_type: {result_type.spelling}')
            result_type_name = result_type.spelling.split(' ')[0]

            if result_type_name in self.wrapped:
                result_type_name = self.wrapped[result_type_name].gen_wrapper['type']
                result = f"new {result_type_name}({result})"

            with self:
                self(f"{ret}{result};")
                self(f"return {self.get_function_result(node, cursor)};")
            self("}")
        else:
            self(f'{mname}.def("{pyname}", {cname}')
        self.write_pyargs(arguments, node)
        self(f", {self.get_return_policy(cursor)});\n")

    def visit_struct(self, cursor):
        if not self.is_class_mappable(cursor):
            return
        node: StructNode = self.lookup_or_create_node(f'struct.{self.spell(cursor)}', cursor=cursor)
        #TODO: I added this because structures were getting visited twice.  It's new, so keep an eye on it.
        if node.visited:
            return
        node.visited = True

        fqname = node.fqname
        pyname = node.pyname

        if fqname == pyname:
            logger.debug(f"fqname == pyname: {fqname}")
            exit()
        if not pyname:
            return

        #logger.debug(entry)
        children = list(cursor.get_children())  # it's an iterator
        wrapped = False
        # Handle the case of a struct with one enum child
        if len(children) == 1:
            first_child = children[0]
            wrapped = first_child.kind == cindex.CursorKind.ENUM_DECL
        if not wrapped:
            base = None
            for child in cursor.get_children():
                if child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                    base = child
            if base:
                basename = self.spell(base)
                self(f"PYSUBCLASS_BEGIN({self.module}, {fqname}, {basename}, {pyname})")
            else:
                self(f"PYCLASS_BEGIN({self.module}, {fqname}, {pyname})")
        with self.enter(node):
            #TODO: this is a can of worms trying to map substructures.  Might be worth it if I can figure it out.
            # May add a flag to the yaml to indicate whether to map substructures or not.  example: traverse: shallow|deep
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        if not wrapped:
            self(f"PYCLASS_END({self.module}, {fqname}, {pyname})\n")

    def visit_class(self, cursor):
        if not self.is_class_mappable(cursor):
            return
        node: ClassNode = self.lookup_or_create_node(f'class.{self.spell(cursor)}', cursor=cursor)
        #logger.debug(entry)
        self(f"PYCLASS_BEGIN({self.module}, {node.fqname}, {node.pyname})")
        with self.enter(node):
            self.visit_children(cursor)

            if node.gen_init:
                self.gen_init()
            elif node.gen_kw_init:
                self.gen_kw_init()

        self(f"PYCLASS_END({self.module}, {node.fqname}, {node.pyname})\n")

    def gen_init(self):
        self(f"{self.scope}.def(py::init<>());")

    def gen_kw_init(self):
        node = self.top_node
        self(f'{self.scope}.def(py::init([](const py::kwargs& kwargs)')
        self("{")
        with self:
            self(f'{node.fqname} obj;')
            for child in node.children:
                cursor = child.cursor
                typename = None
                is_char_ptr = self.is_char_ptr(cursor)
                if is_char_ptr:
                    typename = 'std::string'
                else:
                    typename = cursor.type.spelling
                if type(child) is FieldNode:
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


    def visit_var(self, cursor):
        #logger.debug(f"Not implemented:  visit_var: {cursor.spelling}")
        pass

    def visit_using_decl(self, cursor):
        #logger.debug(f"Not implemented:  visit_using_decl: {cursor.spelling}")
        pass

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

    # TODO: This is a mess
    def visit_overloads(self, cursor):
        for child in cursor.get_children():
            if child.kind in [
                cindex.CursorKind.CXX_METHOD,
                cindex.CursorKind.FUNCTION_DECL,
            ]:
                key = self.spell(child)
                if key in self.overloaded.visited:
                    self.overloaded.add(key)
                else:
                    self.overloaded.visited.add(key)
            elif self.is_cursor_mappable(child):
                self.visit_overloads(child)
