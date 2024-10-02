from typing import Optional

from pathlib import Path

from loguru import logger

from .unit_base_factory import UnitBaseFactory
from ..unit import Unit
from ..loader.unit_loader import UnitLoader

class UnitFactory(UnitBaseFactory):
    def __init__(self) -> None:
        self.unit: Optional[Unit] = None

    def load(self, path: Path) -> Unit:
        unit = UnitLoader().load(path)
        return unit