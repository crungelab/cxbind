from cxbind.unit import Unit

from ..backend.pb.pb_backend import PbBackend
from ..node import Root

from .program import Program


class PbProgram(Program):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.backend = PbBackend(self)
