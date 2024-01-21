import os, sys

from pathlib import Path
import importlib.util
from loguru import logger
from clang import cindex

from . import generator as dot_cxbind

class Runner:
    def __init__(self):
        if sys.platform == 'darwin':
            cindex.Config.set_library_path('/usr/local/opt/llvm@6/lib')
        elif sys.platform == 'linux':
            #TODO: make this configurable
            cindex.Config.set_library_file('/usr/lib/llvm-15/lib/libclang.so.1')
        else:
            cindex.Config.set_library_path('C:/Program Files/LLVM/bin')

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

        generator = dot_cxbind.Generator.create(name)
        generator.generate()

    def gen_all(self):
        path = Path(os.getcwd(), '.cxbind')
        if not path.exists():
            print('No .cxbind directory found.')
            return
        files = path.glob('*.yaml')
        for file in files:
            self.gen(file.stem)