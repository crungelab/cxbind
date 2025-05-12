from typing import Protocol, Any

class GeneratorProtocol(Protocol):
    def generate(self) -> None:
        ...
