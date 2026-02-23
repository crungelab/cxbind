from loguru import logger

from .task import Task


class Phase(Task):
    def __init__(self) -> None:
        super().__init__()
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.priority)

    def run(self) -> None:
        for task in self.tasks:
            task.run()

class BuildPhase(Phase):
    def __init__(self):
        super().__init__()
        self.priority = 10

class TransformPhase(Phase):
    def __init__(self):
        super().__init__()
        self.priority = 20

class GeneratePhase(Phase):
    def __init__(self):
        super().__init__()
        self.priority = 30