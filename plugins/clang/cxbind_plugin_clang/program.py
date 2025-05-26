import os
from pathlib import Path

import jinja2
from rich import print

from cxbind.program_base import ProgramBase
from cxbind.unit import Unit

from .generator import Generator


class Program(ProgramBase):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)

        BASE_PATH = Path('.')
        config_searchpath = BASE_PATH  / '.cxbind' / 'templates'
        default_searchpath = Path(os.path.dirname(os.path.abspath(__file__)), 'templates')
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

    def run(self):
        """
        Run the program.
        """
        sources = self.unit.sources
        if self.unit.source is not None:
            sources.append(self.unit.source)

        text_list = []

        for source in sources:
            generator = Generator(source, self.unit)
            text_list.append(generator.generate())

        text = "\n".join(text_list)

        #Jinja
        context = {
            'body': text
        }

        unit_template_path = self.unit.template

        if unit_template_path:
            template = self.jinja_env.get_template(unit_template_path)
        else:
            template = self.jinja_env.get_template(f'{self.unit.name}.cpp')

        rendered = template.render(context)

        filename = self.unit.target
        with open(filename,'w') as fh:
            fh.write(rendered)

        print(f'[bold green]Generated[/bold green]: {filename}', ':thumbs_up:')

    '''
    def run(self):
        """
        Run the program.
        """
        generator = Generator(self.unit)
        generator.generate()
    '''