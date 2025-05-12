class GeneratorFactory:
    def __init__(self, cls):
        self.cls = cls

    def produce(self, unit):
        """
        Create an instance of the generator class.
        """
        return self.cls(unit)
