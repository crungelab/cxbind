"""A progress bar for a cxbind run: one step per task (a unit), plus the final plan.

Shown only on a terminal: when cxtest or CI captures the output, nothing is drawn,
so logs don't fill up with redraws. Lines printed during the run (the
created/updated lines) appear above the bar, which disappears when the run ends.
"""

from __future__ import annotations

from rich import get_console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Column


class RunProgress:
    def __init__(self, total: int, title: str = "cxbind") -> None:
        self.total = total
        self.title = title
        self.progress: Progress | None = None
        self.task: TaskID | None = None

    def __enter__(self) -> "RunProgress":
        console = get_console()  # the console rich.print uses: printed lines go above the bar
        if console.is_terminal:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.fields[title]}"),
                BarColumn(bar_width=30),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                TextColumn("[dim]{task.description}", table_column=Column(no_wrap=True, overflow="ellipsis")),
                console=console,
                transient=True,
            )
            self.progress.start()
            self.task = self.progress.add_task("", total=self.total, title=self.title)
        return self

    def __exit__(self, *exc) -> None:
        if self.progress is not None:
            self.progress.stop()

    def working_on(self, description: str) -> None:
        if self.progress is not None:
            self.progress.update(self.task, description=description)

    def advance(self) -> None:
        if self.progress is not None:
            self.progress.advance(self.task)


def task_name(task: object) -> str:
    """What to show for a task: its unit's name when it has one."""
    unit = getattr(task, "unit", None)
    return getattr(unit, "name", None) or type(task).__name__
