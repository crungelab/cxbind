from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .compiler import Compiler

class Processor(ABC):
    def __init__(self, compiler: 'Compiler') -> None:
        self.compiler = compiler
        
    @abstractmethod
    def run():
        pass