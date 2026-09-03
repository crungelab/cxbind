from typing import Optional

from loguru import logger

from .task import Task
from .plan import Plan

from ..context import Context
from ..project import Project


class Runner(Context["Runner"]):
    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self._plan: Optional["Plan"] = None

    @property
    def plan(self) -> "Plan":
        if self._plan is None:
            self._plan = Plan()
        return self._plan

    def run(self, tasks: list["Task"]) -> None:
        with self.use():
            for task in tasks:
                task.run()
            self.plan.run()
            self.plan.clear()
