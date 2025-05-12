import sys
from loguru import logger
from clang import cindex

from cxbind import CxBind
from cxbind.plugin import Plugin

from .program import Program

class ClangPlugin(Plugin):
    def __init__(self):
        super().__init__()

    def install(self, app: CxBind):
        if sys.platform == 'darwin':
            cindex.Config.set_library_path('/usr/local/opt/llvm@6/lib')
        elif sys.platform == 'linux':
            #TODO: make this configurable
            cindex.Config.set_library_file('/usr/lib/llvm-17/lib/libclang.so.1')
        else:
            cindex.Config.set_library_path('C:/Program Files/LLVM/bin')

        logger.debug("Installing Clang Plugin")
        app.register_program("clang", Program)