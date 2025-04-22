import os, sys
from pathlib import Path
import importlib.util

from loguru import logger
from clang import cindex

from . import generator as dot_cxbind
from .project import Project
from .unit import Unit
from .factory.project_factory import ProjectFactory


class CxBind:
    def __init__(self):
        self.prj_dir = Path(os.getcwd(), '.cxbind')

        if sys.platform == 'darwin':
            cindex.Config.set_library_path('/usr/local/opt/llvm@6/lib')
        elif sys.platform == 'linux':
            #TODO: make this configurable
            cindex.Config.set_library_file('/usr/lib/llvm-17/lib/libclang.so.1')
        else:
            cindex.Config.set_library_path('C:/Program Files/LLVM/bin')

        log_level = "DEBUG"
        log_format = "<level>{level: <8}</level> | {file}:{line: >4} - {message}"
        #logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
        #logger.add(sys.stderr, level=log_level, colorize=True, backtrace=True, diagnose=True)
        logger.add("cxbind.log", mode="w", level=log_level, format=log_format, colorize=False, backtrace=True, diagnose=True)
        #logger.add("cxbind.log", level=log_level, colorize=False, backtrace=True, diagnose=True)

    def load_project(self) -> Project:
        #prj_dir = Path(os.getcwd(), '.cxbind')
        path = next(self.prj_dir.glob('*.prj.yaml'), None)
        if path is not None:
            project = ProjectFactory().load(path)
        else:
            project = ProjectFactory().create(self.prj_dir, 'default')

        if project.is_empty():
            logger.error('No units found in project.')
            sys.exit(1)

        return project

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
            generator.generate()
