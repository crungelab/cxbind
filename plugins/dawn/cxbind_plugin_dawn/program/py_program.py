from cxbind.unit import Unit

from ..backend.py_backend import PyBackend
from ..node import Root

from .program import Program


class PyProgram(Program):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PyBackend(self)
