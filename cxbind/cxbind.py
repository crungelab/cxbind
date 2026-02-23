from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin import Plugin

import os, sys
from pathlib import Path
from importlib.metadata import entry_points


from loguru import logger

from .project import Project
from .unit import Unit
from .factory.project_factory import ProjectFactory
from .factory.tool_factory import ToolFactory
from .tool import Tool

# TODO: Move this somewhere else
from .transform import Transform
from .transformer import Transformer, _registry as TRANSFORMER_REGISTRY

from .runner.runner_factory import RunnerFactory
from .runner.runner import Runner


class CxBind:
    def __init__(self):
        self.tool_factories: dict[str, ToolFactory] = {}
        self.prj_dir = Path(os.getcwd(), ".cxbind")
        self._runner_factory: RunnerFactory = None
        self.runner: Runner = None

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

    @property
    def runner_factory(self) -> RunnerFactory:
        if self._runner_factory is None:
            logger.error("Runner factory not set. Make sure a plugin has been installed that registers a runner factory.")
            sys.exit(1)
        return self._runner_factory
    
    @runner_factory.setter
    def runner_factory(self, factory: RunnerFactory):
        if self._runner_factory is not None:
            raise Exception("Runner factory already set. Overwriting is not allowed.")
        self._runner_factory = factory

    def install_plugins(self):
        plugin_eps = entry_points(group="cxbind.plugins")
        logger.debug(f"plugin_eps: {plugin_eps}")

        for ep in plugin_eps:
            logger.debug(f"ep: {ep}")
            plugin: Plugin = ep.load()()
            logger.debug(f"plugin: {plugin}")
            plugin.install(self)

    def register_transformer(self, transform_type: type[Transform], cls: type[Transformer]):
        """
        Register a transformer class with a transform type.
        """
        if transform_type in TRANSFORMER_REGISTRY:
            logger.warning(f"Transformer for {transform_type} already registered. Overwriting.")
        TRANSFORMER_REGISTRY[transform_type] = cls

    def register_tool(self, name: str, cls):
        """
        Register a tool class with a name.
        """
        if name in self.tool_factories:
            logger.warning(f"Tool {name} already registered. Overwriting.")
        self.tool_factories[name] = ToolFactory(cls)

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

    def create_tool(self, unit: Unit) -> Tool:
        tool_name = unit.tool
        if tool_name is None:
            tool_name = "clang"

        tool = self.tool_factories[tool_name].produce(unit)
        return tool

    def gen(self, name):
        logger.debug(f"gen: {name}")
        project = self.load_project()
        unit = project.get_unit(name)
        tool = self.create_tool(unit)
        #tool.run()
        runner_factory = self.runner_factory(tool)
        runner = runner_factory()
        runner.run([tool])

    def gen_all(self):
        path = Path(os.getcwd(), ".cxbind")
        if not path.exists():
            print("No .cxbind directory found.")
            return

        project = self.load_project()

        tools: list[Tool] = []
        for unit in project.units.values():
            tool = self.create_tool(unit)
            logger.debug(f"Generating {unit.name} with {tool.__class__.__name__}")
            logger.debug(f"unit: {unit}")
            tools.append(tool)

        runner = self.runner_factory()
        runner.run(tools)

    """
    def gen(self, name):
        logger.debug(f"gen: {name}")
        project = self.load_project()
        unit = project.get_unit(name)
        tool = self.create_tool(unit)
        tool.run()

    def gen_all(self):
        path = Path(os.getcwd(), ".cxbind")
        if not path.exists():
            print("No .cxbind directory found.")
            return

        project = self.load_project()

        for unit in project.units.values():
            tool = self.create_tool(unit)
            logger.debug(f"Generating {unit.name} with {tool.__class__.__name__}")
            logger.debug(f"unit: {unit}")
            tool.run()
    """