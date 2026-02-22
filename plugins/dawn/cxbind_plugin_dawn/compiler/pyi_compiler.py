from cxbind.unit import Unit

from ..backend.pyi.pyi_backend import PyiBackend
from ..node import Root

from .compiler import Compiler


class PyiCompiler(Compiler):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PyiBackend(self)
