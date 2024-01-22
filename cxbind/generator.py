import os
from pathlib import Path
import importlib
from loguru import logger
import jinja2

from clang import cindex

from .yaml import load_yaml

from . import UserSet


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
        #self.excluded = set(self.excludes)
        self.context.excluded = set(self.excludes)
        #self.overloaded = Overloaded(self.overloads)
        self.context.overloaded = Overloaded(self.overloads)

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

        #self.actions = __actions__.MAP
        Builder.actions = __actions__.MAP

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
