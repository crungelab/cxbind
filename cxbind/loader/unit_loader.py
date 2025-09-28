from typing import Optional

from pathlib import Path

from loguru import logger

from .unit_base_loader import UnitBaseLoader
from ..unit import Unit


class UnitLoader(UnitBaseLoader):
    def __init__(self) -> None:
        self.unit: Optional[Unit] = None

    def load(self, path: Path) -> Unit:
        data = self.load_yaml(path)

        # Validate with Pydantic
        unit = Unit.model_validate(data)

        if unit.name is None:
            #unit.name = path.stem
            unit.name = path.stem.split('.')[0]

        logger.debug(f"unit: {unit}")

        return unit
