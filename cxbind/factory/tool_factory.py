class ToolFactory:
    def __init__(self, cls):
        self.cls = cls

    def produce(self, unit):
        """
        Create an instance of the program class.
        """
        return self.cls(unit)
