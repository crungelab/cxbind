from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .program import Program

class Processor(ABC):
    def __init__(self, program: 'Program') -> None:
        self.program = program
        
    @abstractmethod
    def run():
        pass