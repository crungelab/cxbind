from cxbind.unit import Unit

from ..backend.py.py_backend import PyBackend
from ..node import Root

from .compiler import Compiler


class PyCompiler(Compiler):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PyBackend(self)
