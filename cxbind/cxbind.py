from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin import Plugin

import os
from pathlib import Path
from importlib.metadata import entry_points

from loguru import logger

from .project import Project
from .unit import Unit
from .factory.project_factory import ProjectFactory
from .tool import Tool
from .runner.runner_factory import RunnerFactory
from .manifest import Manifest
from .outputs import Outputs
from .report import Report, REPORT_NAME

DEFAULT_RUNNER = "clang"


class CxBindError(Exception):
    """A user-facing error: no project, unknown unit, missing plugin.

    Raised instead of exiting so CxBind can be used from other Python code;
    the CLI turns it into a message and a nonzero exit status.
    """


class CxBind:
    """The cxbind application: plugins, project loading, generation.

    Runs in the current directory, which must be the project directory:
    target paths in project files are relative to it.
    """

    def __init__(self) -> None:
        self.project_dir = Path(os.getcwd())
        self.cxbind_dir = self.project_dir / ".cxbind"
        self.state_dir = self.project_dir / "_cxbind"   # generated per run; gitignored
        self.runner_factories: dict[str, RunnerFactory] = {}
        self.install_plugins()

    # --- plugins ---------------------------------------------------------

    def install_plugins(self) -> None:
        for ep in entry_points(group="cxbind.plugins"):
            logger.debug(f"Installing plugin: {ep}")
            plugin: "Plugin" = ep.load()()
            plugin.install(self)

    def register_runner_factory(self, name: str, factory: RunnerFactory) -> None:
        if name in self.runner_factories:
            logger.warning(f"Runner {name} already registered. Overwriting.")
        self.runner_factories[name] = factory

    # --- project ---------------------------------------------------------

    def load_project(self) -> Project:
        if not self.cxbind_dir.is_dir():
            raise CxBindError(f"No .cxbind directory found in {self.project_dir}")

        path = next(self.cxbind_dir.glob("*.prj.yaml"), None)
        if path is not None:
            project = ProjectFactory().load(path)
        else:
            project = ProjectFactory().create(self.cxbind_dir, "default")

        if project.is_empty():
            raise CxBindError(f"No units found in project ({self.cxbind_dir})")

        return project

    def choose_runner_factory(self, project: Project) -> RunnerFactory:
        runner_name = project.runner or DEFAULT_RUNNER
        factory = self.runner_factories.get(runner_name)
        if factory is None:
            installed = ", ".join(self.runner_factories) or "none"
            raise CxBindError(
                f"Runner '{runner_name}' is not registered (installed: {installed}). "
                f"Make sure a plugin that provides it is installed."
            )
        return factory

    # --- generation ------------------------------------------------------

    def gen(self, name: str, check: bool = False) -> Outputs:
        project = self.load_project()
        unit = project.get_unit(name)
        if unit is None:
            known = ", ".join(project.units) or "none"
            raise CxBindError(f"Unknown unit '{name}' (units: {known})")
        return self.generate(project, [unit], check=check)

    def gen_all(self, check: bool = False) -> Outputs:
        project = self.load_project()
        return self.generate(project, list(project.units.values()), check=check)

    def generate(self, project: Project, units: list[Unit], check: bool = False) -> Outputs:
        """Generate `units`. With check=True nothing is written: the returned Outputs
        (and the report) say what would change."""
        runner_factory = self.choose_runner_factory(project)

        tools: list[Tool] = []
        for unit in units:
            tool = runner_factory.create_tool(unit)
            logger.debug(f"Generating {unit.name} with {tool.__class__.__name__}")
            tools.append(tool)

        runner = runner_factory.produce(project)

        # Only a run of every unit can tell orphans (files no longer generated)
        # from files another unit produces.
        complete = len(units) == len(project.units)
        report = Report(self.project_dir, project.name or self.project_dir.name, check=check)
        outputs = Outputs(self.project_dir, Manifest(self.state_dir), check=check, complete=complete)
        # Outputs.active() reads the previous manifest and (in a complete normal run)
        # resets it, only once generation is really about to happen: a config error
        # above shouldn't wipe the record of the last successful run.
        try:
            with report.active(), outputs.active():
                runner.run(tools)
                outputs.finish()
        finally:
            report.write(self.state_dir / REPORT_NAME)
        return outputs
