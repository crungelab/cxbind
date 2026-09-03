from loguru import logger

from cxbind import CxBind
from cxbind.plugin import Plugin
from .dawn_runner_factory import DawnRunnerFactory


class DawnPlugin(Plugin):
    def __init__(self):
        super().__init__()

    def install(self, app: CxBind):
        logger.debug("Installing Dawn Plugin")

        app.register_runner_factory("dawn", DawnRunnerFactory())

    """
    def install(self, app: CxBind):
        logger.debug("Installing Dawn Plugin")

        app.runner_factory = RunnerFactory(Runner)
        
        app.register_tool("dawn_hpp", HppCompiler)
        app.register_tool("dawn_cpp", CppCompiler)
        app.register_tool("dawn_pb", PbCompiler)
        app.register_tool("dawn_py", PyCompiler)
        app.register_tool("dawn_pyi", PyiCompiler)
        
    """