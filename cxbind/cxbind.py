from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin import Plugin

import os, sys
from pathlib import Path
import importlib.util
from importlib.metadata import entry_points


from loguru import logger

#from . import generator as dot_cxbind
from .project import Project
from .unit import Unit
from .factory.project_factory import ProjectFactory
from .factory.generator_factory import GeneratorFactory
from .generator_protocol import GeneratorProtocol

class CxBind:
    def __init__(self):
        self.generator_factories: dict[str, GeneratorFactory] = {}
        self.prj_dir = Path(os.getcwd(), '.cxbind')

        log_level = "DEBUG"
        log_format = "<level>{level: <8}</level> | {file}:{line: >4} - {message}"
        #logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
        #logger.add(sys.stderr, level=log_level, colorize=True, backtrace=True, diagnose=True)
        logger.add("cxbind.log", mode="w", level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)
        #logger.add("cxbind.log", level=log_level, colorize=False, backtrace=True, diagnose=True)

        self.install_plugins()

    def install_plugins(self):
        plugin_eps = entry_points(group="cxbind.plugins")
        print("plugin_eps", plugin_eps)


        for ep in plugin_eps:
            print("ep", ep)

            plugin: Plugin = ep.load()()
            print("plugin", plugin)
            plugin.install(self)

    def register_generator(self, name: str, cls):
        """
        Register a generator class with a name.
        """
        if name in self.generator_factories:
            logger.warning(f"Generator {name} already registered. Overwriting.")
        self.generator_factories[name] = GeneratorFactory(cls)

    def load_project(self) -> Project:
        path = next(self.prj_dir.glob('*.prj.yaml'), None)
        if path is not None:
            project = ProjectFactory().load(path)
        else:
            project = ProjectFactory().create(self.prj_dir, 'default')

        if project.is_empty():
            logger.error('No units found in project.')
            sys.exit(1)

        return project

    def create_generator(self, unit: Unit) -> GeneratorProtocol:
        """
        Create a generator instance for the given unit.
        This method is responsible for loading the generator class dynamically.
        """
        generator_name = unit.generator
        if generator_name is None:
            generator_name = "clang"

        generator = self.generator_factories[generator_name].produce(unit)
        return generator
    '''
    def create_generator(self, unit: Unit):
        global dot_cxbind
        path = Path(os.getcwd(), '.cxbind', '__init__.py')
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(
                "dot_cxbind", path
            )
            dot_cxbind = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dot_cxbind)

        generator = dot_cxbind.Generator.produce(unit)
        return generator
    '''

    def gen(self, name):
        logger.debug(f"gen: {name}")
        project = self.load_project()
        unit = project.get_unit(name)
        generator = self.create_generator(unit)
        generator.generate()

    def gen_all(self):
        path = Path(os.getcwd(), '.cxbind')
        if not path.exists():
            print('No .cxbind directory found.')
            return
        
        project = self.load_project()

        for unit in project.units.values():
            generator = self.create_generator(unit)
            logger.debug(f"Generating {unit.name} with {generator.__class__.__name__}")
            generator.generate()
