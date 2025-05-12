from cxbind.program_base import ProgramBase
from cxbind.unit import Unit

from .generator import Generator


class Program(ProgramBase):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)

    def run(self):
        """
        Run the program.
        """
        generator = Generator(self.unit)
        generator.generate()