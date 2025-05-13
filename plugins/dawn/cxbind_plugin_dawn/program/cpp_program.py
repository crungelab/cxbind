from cxbind.unit import Unit

from ..backend.cpp.cpp_backend import CppBackend
from ..node import Root

from .program import Program


class CppProgram(Program):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = CppBackend(self)
