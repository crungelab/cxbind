import os
from pathlib import Path
import importlib
from loguru import logger
import jinja2

from clang import cindex

from .yaml import load_yaml


from .generator_config import GeneratorConfig
from .builder import Builder
from .builder_context import BuilderContext


class Generator(Builder):
    def __init__(self, name: str, config: GeneratorConfig, **kwargs):
        super().__init__(BuilderContext(config, **kwargs))
        logger.debug(f"Generator: {name}")
        self.name = name
        self.config = config

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

        Builder.actions = __actions__.MAP

    def generate(self):
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
