import os
from pathlib import Path
import importlib
from loguru import logger
from rich import print

import jinja2

from clang import cindex

from .unit import Unit
from .builder import Builder
from .builder_context import BuilderContext


class Generator(Builder):
    def __init__(self, unit: Unit, **kwargs):
        super().__init__(BuilderContext(unit, **kwargs))

        BASE_PATH = Path('.')
        self.path = BASE_PATH / self.source
        self.mapped.append(self.path.name)

        config_searchpath = BASE_PATH  / '.cxbind' / 'templates'
        default_searchpath = Path(os.path.dirname(os.path.abspath(__file__)), 'templates')
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)


    @classmethod
    def produce(self, unit: Unit):
        instance = Generator(unit)
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

        with self.out:
            self.visit_overloads(tu.cursor)
            self.visit_children(tu.cursor)
            self.end_chain()

        #Jinja
        context = {
            'body': self.text
        }
        unit_template_path = self.unit.template
        if unit_template_path:
            template = self.jinja_env.get_template(unit_template_path)
        else:
            template = self.jinja_env.get_template(f'{self.unit.name}.cpp')

        rendered = template.render(context)
        filename = self.target
        with open(filename,'w') as fh:
            fh.write(rendered)

        print(f'[bold green]Generated[/bold green]: {filename}', ':thumbs_up:')

    def visit_overloads(self, cursor):
        for child in cursor.get_children():
            if child.kind in [
                cindex.CursorKind.CONSTRUCTOR,
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
