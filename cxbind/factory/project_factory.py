from typing import List, Optional
import os
from pathlib import Path

from loguru import logger

from .unit_base_factory import UnitBaseFactory
from .unit_factory import UnitFactory

from ..project import Project
from ..unit import Unit

from ..loader.project_loader import ProjectLoader
from ..configurator.project_configurator import ProjectConfigurator


class ProjectFactory(UnitBaseFactory):
    def __init__(self) -> None:
        self.project: Optional[Project] = None

    def load(self, path: Path) -> Project:
        project = ProjectLoader().load(path)
        ProjectConfigurator(project).configure()
        return project

    def create(self, directory: Path, name: str) -> Project:
        files = directory.glob('*.unit.yaml')
        unit_files = [{'path': file} for file in files]
        logger.debug(f"unit_files: {unit_files}")
        path = Path(os.getcwd(), '.cxbind', f'{name}.prj.yaml')
        data = {
            'name': name,
            'unit_files': unit_files,
            'path': path
        }
        project = Project.model_validate(data)
        logger.debug(f"project: {project}")
        ProjectConfigurator(project).configure()
        return project
