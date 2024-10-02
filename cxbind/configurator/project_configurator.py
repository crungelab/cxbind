from pathlib import Path
from loguru import logger

from ..project import Project
from ..unit import Unit
from ..factory.unit_factory import UnitFactory
from .unit_configurator import UnitConfigurator


class ProjectConfigurator:
    def __init__(self, project: Project) -> None:
        self.project = project

    def configure(self):
        project = self.project

        for unit_file in project.unit_files:
            #logger.debug(f"unit_file: {unit_file}")
            unit_path = project.path.parent / unit_file.path
            self.load_unit(unit_path)

        for unit in project.units.values():
            UnitConfigurator(project, unit).configure()

        return project

    def load_unit(self, path: Path) -> Unit:
        project = self.project
        unit = UnitFactory().load(path)
        project.add_unit(unit)
        return unit