from typing import Optional

from loguru import logger

from .runner import Runner

from ..unit import Unit
from ..project import Project

from ..tool import Tool

from ..transform import Transform
from ..transformer import Transformer, _registry as TRANSFORMER_REGISTRY

from ..factory.tool_factory import ToolFactory

class RunnerFactory:
    def __init__(self, cls: type[Runner]) -> None:
        self.cls = cls

        self.tool_factories: dict[str, ToolFactory] = {}


    def produce(self, project: Project) -> Runner:
        """
        Create an instance of the runner class.
        """
        return self.cls(project)

    def register_tool(self, name: str, cls: type[Tool]):
        """
        Register a tool class with a name.
        """
        if name in self.tool_factories:
            logger.warning(f"Tool {name} already registered. Overwriting.")
        self.tool_factories[name] = ToolFactory(cls)

    def create_tool(self, unit: Unit) -> Tool:
        tool_name = unit.tool
        if tool_name is None:
            tool_name = "clang"

        tool = self.tool_factories[tool_name].produce(unit)
        return tool

    def register_transformer(self, transform_type: type[Transform], cls: type[Transformer]):
        """
        Register a transformer class with a transform type.
        """
        if transform_type in TRANSFORMER_REGISTRY:
            logger.warning(f"Transformer for {transform_type} already registered. Overwriting.")
        TRANSFORMER_REGISTRY[transform_type] = cls
