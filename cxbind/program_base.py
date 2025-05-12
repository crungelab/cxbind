from cxbind.unit import Unit


class ProgramBase():
    def __init__(self, unit: Unit) -> None:
        self.unit = unit

    def run(self):
        pass