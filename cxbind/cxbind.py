from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin import Plugin

import os, sys
from pathlib import Path
from importlib.metadata import entry_points

from loguru import logger

from .project import Project
from .factory.project_factory import ProjectFactory
from .tool import Tool

from .runner.runner_factory import RunnerFactory
from .runner.runner import Runner


class CxBind:
    def __init__(self):
        self.runner_factories: dict[str, RunnerFactory] = {}
        self.prj_dir = Path(os.getcwd(), ".cxbind")

        log_level = "DEBUG"
        log_format = "<level>{level: <8}</level> | {file}:{line: >4} - {message}"
        # logger.add(sys.stderr, level=log_level, format=log_format, colorize=True, backtrace=True, diagnose=True)
        # logger.add(sys.stderr, level=log_level, colorize=True, backtrace=True, diagnose=True)
        logger.add(
            "cxbind.log",
            mode="w",
            level=log_level,
            format=log_format,
            colorize=False,
            backtrace=True,
            diagnose=True,
        )
        # logger.add("cxbind.log", level=log_level, colorize=False, backtrace=True, diagnose=True)

        self.install_plugins()

    def install_plugins(self):
        plugin_eps = entry_points(group="cxbind.plugins")
        logger.debug(f"plugin_eps: {plugin_eps}")

        for ep in plugin_eps:
            logger.debug(f"ep: {ep}")
            plugin: Plugin = ep.load()()
            logger.debug(f"plugin: {plugin}")
            plugin.install(self)


    def register_runner_factory(self, name: str, factory: RunnerFactory):
        """
        Register a runner class with a name.
        """
        if name in self.runner_factories:
            logger.warning(f"Runner {name} already registered. Overwriting.")
        self.runner_factories[name] = factory

    def load_project(self) -> Project:
        path = next(self.prj_dir.glob("*.prj.yaml"), None)
        if path is not None:
            project = ProjectFactory().load(path)
        else:
            project = ProjectFactory().create(self.prj_dir, "default")

        if project.is_empty():
            logger.error("No units found in project.")
            sys.exit(1)

        return project

    def choose_runner_factory(self, project: Project) -> RunnerFactory:
        runner_name = project.runner
        if runner_name is None:
            runner_name = "clang"

        if runner_name not in self.runner_factories:
            logger.error(f"Runner {runner_name} not registered. Make sure a plugin has been installed that registers this runner.")
            sys.exit(1)

        return self.runner_factories[runner_name]

    def gen(self, name):
        logger.debug(f"gen: {name}")

        project = self.load_project()
        unit = project.get_unit(name)

        runner_factory = self.choose_runner_factory(project)
        tool = runner_factory.create_tool(unit)
        logger.debug(f"Generating {unit.name} with {tool.__class__.__name__}")

        runner = runner_factory.produce(project)
        runner.run([tool])

    def gen_all(self):
        path = Path(os.getcwd(), ".cxbind")
        if not path.exists():
            print("No .cxbind directory found.")
            return

        project = self.load_project()

        runner_factory = self.choose_runner_factory(project)

        tools: list[Tool] = []
        for unit in project.units.values():
            tool = runner_factory.create_tool(unit)
            logger.debug(f"Generating {unit.name} with {tool.__class__.__name__}")
            logger.debug(f"unit: {unit}")

            tools.append(tool)

        runner = runner_factory.produce(project)
        runner.run(tools)
