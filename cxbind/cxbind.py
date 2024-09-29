import os, sys

from pathlib import Path
import importlib.util
from loguru import logger
from clang import cindex

from . import generator as dot_cxbind
from .project import Project
from .unit import Unit
from .loader.project_loader import ProjectLoader


class CxBind:
    def __init__(self):
        if sys.platform == 'darwin':
            cindex.Config.set_library_path('/usr/local/opt/llvm@6/lib')
        elif sys.platform == 'linux':
            #TODO: make this configurable
            cindex.Config.set_library_file('/usr/lib/llvm-17/lib/libclang.so.1')
        else:
            cindex.Config.set_library_path('C:/Program Files/LLVM/bin')

    def load_project(self):
        path = Path(os.getcwd(), '.cxbind', 'project.yaml')
        project = ProjectLoader().load(path)
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
        for unit in project.units:
            generator = self.create_generator(unit)
            generator.generate()

    '''
    def gen(self, name):
        logger.debug(f"gen: {name}")
        global dot_cxbind
        path = Path(os.getcwd(), '.cxbind', '__init__.py')
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(
                "dot_cxbind", path
            )
            dot_cxbind = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dot_cxbind)

        generator = dot_cxbind.Generator.produce(name)
        generator.generate()

    def gen_all(self):
        path = Path(os.getcwd(), '.cxbind')
        if not path.exists():
            print('No .cxbind directory found.')
            return
        files = path.glob('*.yaml')
        for file in files:
            self.gen(file.stem)
    '''