from typing import List, Optional
from pathlib import Path
import yaml

from loguru import logger
from pydantic import BaseModel, Field

from .node import FunctionNode, MethodNode, StructNode, ClassNode, FieldNode, CtorNode
from .unit_base import UnitBase
from .unit import Unit


class UnitFile(BaseModel):
    path: Path


class Project(UnitBase):
    unit_files: list[UnitFile]

    path: Path = Field(None, exclude=True, repr=False)
    units: list[Unit] = Field([], exclude=True, repr=False)
    units_by_name: dict[str, Unit] = Field({}, exclude=True, repr=False)

    def add_unit(self, unit: Unit):
        self.units.append(unit)
        self.units_by_name[unit.name] = unit

    def get_unit(self, name: str) -> Optional[Unit]:
        return self.units_by_name.get(name)
