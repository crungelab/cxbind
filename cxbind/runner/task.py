from loguru import logger

#from .runner import Runner


class Task:
    def __init__(self) -> None:
        super().__init__()
        self.priority: int = 0

    """
    @property
    def current_runner(self) -> Runner:
        return Runner.get_current()
    """

    def clear(self) -> None:
        pass

    def run(self) -> None:
        pass


class LambdaTask(Task):
    def __init__(self, func: callable) -> None:
        super().__init__()
        self.func = func

    def run(self) -> None:
        self.func()