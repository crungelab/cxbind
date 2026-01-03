from cxbind.unit import Unit

from ..backend.pyi.pyi_backend import PyiBackend
from ..node import Root

from .program import Program


class PyiProgram(Program):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PyiBackend(self)
