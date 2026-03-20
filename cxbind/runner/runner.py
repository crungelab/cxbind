from typing import TYPE_CHECKING, Generator
from typing import Optional
import contextlib
from contextvars import ContextVar

from loguru import logger

from .task import Task
from .plan import Plan

#current_runner: ContextVar[Optional["Runner"]] = ContextVar("runner", default=None)

from ..context import Context


class Runner(Context["Runner"]):
    def __init__(self) -> None:
        super().__init__()
        self._plan: Optional["Plan"] = None

    @property
    def plan(self) -> "Plan":
        if self._plan is None:
            self._plan = Plan()
        return self._plan

    """
    @contextlib.contextmanager
    def use(self):
        token = current_runner.set(self)
        try:
            yield self
        finally:
            current_runner.reset(token)

    def make_current(self):
        current_runner.set(self)

    @classmethod
    def get_current(cls) -> Optional["Runner"]:
        return current_runner.get()

    @contextlib.contextmanager
    def use(self):
        prev_runner = self.get_current()
        self.make_current()
        yield self
        if prev_runner is not None:
            prev_runner.make_current()
    """

    def run(self, tasks: list["Task"]) -> None:
        with self.use():
            for task in tasks:
                task.run()
            self.plan.run()
            self.plan.clear()
