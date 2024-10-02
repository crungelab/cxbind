from typing import List, Optional
from pathlib import Path
import yaml

from loguru import logger
from pydantic import BaseModel, Field

from .unit_base import UnitBase
from .unit import Unit, UnitDict


class UnitFile(BaseModel):
    path: Path


class Project(UnitBase):
    unit_files: list[UnitFile] = {}
    #units: dict[str, Unit] = {}
    units: UnitDict = {}

    path: Path = Field(None, exclude=True, repr=False)

    def add_unit(self, unit: Unit):
        self.units[unit.name] = unit

    def get_unit(self, name: str) -> Optional[Unit]:
        return self.units.get(name)
    
    def is_empty(self) -> bool:
        return not bool(self.units)
