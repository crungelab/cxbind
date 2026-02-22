from cxbind.unit import Unit

from ..backend.hpp.hpp_backend import HppBackend
from ..node import Root

from .compiler import Compiler


class HppCompiler(Compiler):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = HppBackend(self)
