from cxbind.unit import Unit

from ..backend.pb.pb_backend import PbBackend
from ..node import Root

from .compiler import Compiler


class PbCompiler(Compiler):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PbBackend(self)
