from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..project import Project

from pathlib import Path

from loguru import logger

from .unit_base_loader import UnitBaseLoader
from ..unit import Unit


class UnitLoader(UnitBaseLoader):
    def __init__(self, project: "Project") -> None:
        self.project = project
        self.unit: Optional[Unit] = None

    def load(self, path: Path) -> Unit:
        project = self.project
        data = self.load_yaml(path)

        # Validate with Pydantic
        unit = Unit.model_validate(data)

        if unit.name is None:
            unit.name = path.stem

        if unit.module is None:
            if project.module is not None:
                unit.module = project.module
            else:
                raise ValueError("module is required")
            
        if unit.flags is None:
            if project.flags is not None:
                unit.flags = project.flags
            else:
                raise ValueError("flags are required")
            
        #unit.prefixes = project.prefixes + unit.prefixes
        # Order needs to be from specific to generic.  Example: prefixes: [SDL_EVENT_, SDL_]
        unit.prefixes = unit.prefixes + project.prefixes

        logger.debug(f"unit: {unit}")

        return unit
