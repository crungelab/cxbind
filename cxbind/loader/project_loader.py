from typing import List, Optional
from pathlib import Path

from loguru import logger

from .unit_base_loader import UnitBaseLoader

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

        #logger.debug(f"project: {project}")

        return project
