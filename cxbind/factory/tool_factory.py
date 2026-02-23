from ..tool import Tool

class ToolFactory:
    def __init__(self, cls: type[Tool]) -> None:
        self.cls = cls

    def __call__(self, *args, **kwargs) -> Tool:
        return self.cls(*args, **kwargs)
    
    def produce(self, unit) -> Tool:
        """
        Create an instance of the tool class.
        """
        return self.cls(unit)
