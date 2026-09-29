from typing import Optional

from loguru import logger

from .task import Task
from .plan import Plan

from ..context import Context
from ..project import Project
from ..progress import RunProgress, task_name


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
        # One step per task (a unit), plus one for the plan: the deferred work,
        # such as assembling stubs from several units.
        with self.use(), RunProgress(len(tasks) + 1) as progress:
            for task in tasks:
                progress.working_on(task_name(task))
                task.run()
                progress.advance()
            progress.working_on("assembling outputs")
            self.plan.run()
            progress.advance()
            self.plan.clear()