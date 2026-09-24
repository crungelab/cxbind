from cxbind.runner.runner_factory import RunnerFactory

from .clang_runner import ClangRunner
from .compiler import Compiler
from .transform import Mogrify
from .transformer import MogrifyTransformer

class ClangRunnerFactory(RunnerFactory):
     def __init__(self):
        super().__init__(ClangRunner)

        self.register_tool("clang", Compiler)
        self.register_transformer(Mogrify, MogrifyTransformer)
