from cxbind.unit import Unit

from ..backend.hpp_backend import HppBackend
from ..node import Root

from .program import Program


class HppProgram(Program):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = HppBackend(self)
