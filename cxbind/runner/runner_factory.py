from typing import Optional

from loguru import logger

from .runner import Runner

class RunnerFactory:
    def __init__(self, cls: type[Runner]) -> None:
        self.cls = cls

    def __call__(self) -> Runner:
        return self.cls()
