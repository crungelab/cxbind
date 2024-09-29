from typing import List, Optional
from pathlib import Path

from loguru import logger

from .unit_base_loader import UnitBaseLoader
from .unit_loader import UnitLoader

from ..project import Project
from ..unit import Unit


class ProjectLoader(UnitBaseLoader):
    def __init__(self) -> None:
        self.project: Optional[Project] = None

    def load(self, path: Path) -> Project:
        data = self.load_yaml(path)

        # Validate with Pydantic
        self.project = project = Project.model_validate(data)

        project.path = path

        if project.name is None:
            project.name = path.stem

        logger.debug(f"project: {project}")

        for unit_file in project.unit_files:
            unit_path = path.parent / unit_file.path
            self.load_unit(unit_path)

        return project

    def load_unit(self, path: Path) -> Unit:
        project = self.project
        unit = UnitLoader(project).load(path)
        project.add_unit(unit)
        return unit