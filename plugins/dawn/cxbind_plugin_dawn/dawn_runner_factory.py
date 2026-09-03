from cxbind.runner import RunnerFactory, Runner

from .compiler import Compiler, HppCompiler, CppCompiler, PbCompiler, PyCompiler, PyiCompiler

class DawnRunnerFactory(RunnerFactory):
     def __init__(self):
        super().__init__(Runner)

        self.register_tool("dawn_hpp", HppCompiler)
        self.register_tool("dawn_cpp", CppCompiler)
        self.register_tool("dawn_pb", PbCompiler)
        self.register_tool("dawn_py", PyCompiler)
        self.register_tool("dawn_pyi", PyiCompiler)

