from cxbind.program_base import ProgramBase
from cxbind.unit import Unit

from ..frontend import Frontend
from ..backend import Backend
from ..node import Root, Entry


class Program(ProgramBase):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.root: Root = None  # Set by Frontend
        self.frontend = Frontend(self)
        self.backend: Backend = None

    def lookup(self, name: str) -> Entry:
        return self.root[name]

    def run(self):
        self.frontend.run()
        self.backend.run()
