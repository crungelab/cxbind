import sys
from loguru import logger

from cxbind import CxBind
from cxbind.plugin import Plugin

from .program import Program, HppProgram, CppProgram, PbProgram, PyProgram


class DawnPlugin(Plugin):
    def __init__(self):
        super().__init__()

    def install(self, app: CxBind):
        logger.debug("Installing Dawn Plugin")
        app.register_program("dawn_hpp", HppProgram)
        app.register_program("dawn_cpp", CppProgram)
        app.register_program("dawn_pb", PbProgram)
        app.register_program("dawn_py", PyProgram)
