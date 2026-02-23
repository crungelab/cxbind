from typing import Generic

from .task import Task
from .phase import Phase


class Plan(Phase):
    def __init__(self) -> None:
        super().__init__()
        self.phases: dict[type[Phase], Phase] = {}

    def add_task(self, child: Task) -> None:
        super().add_task(child)
        if isinstance(child, Phase):
            self.phases[type(child)] = child

    def get_phase(self, phase_type: type[Phase]) -> Phase:
        phase = self.phases.get(phase_type)
        if phase is None:
            phase = phase_type()
            self.add_task(phase)
        return phase

    def clear(self) -> None:
        for child in self.tasks:
            child.clear()

    def run(self) -> None:
        for child in self.tasks:
            child.run()
