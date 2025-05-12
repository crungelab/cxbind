from cxbind.program_base import ProgramBase
from cxbind.unit import Unit

from ..frontend import Frontend
from ..backend import Backend
from ..node import Root


class Program(ProgramBase):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.root: Root = None  # Set by Frontend
        self.frontend = Frontend(self)
        self.backend: Backend = None

    def run(self):
        self.frontend.run()
        self.backend.run()
