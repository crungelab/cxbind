"""cxbind.progress: a bar on a terminal, nothing anywhere else."""

from __future__ import annotations

import io
import re
from types import SimpleNamespace

import pytest
import rich
from rich.console import Console

from cxbind.progress import RunProgress, task_name


@pytest.fixture
def terminal(monkeypatch) -> io.StringIO:
    out = io.StringIO()
    monkeypatch.setattr(rich, "_console", Console(file=out, force_terminal=True, width=100))
    return out


def run(steps: list[str]) -> RunProgress:
    with RunProgress(len(steps)) as progress:
        seen = progress
        for step in steps:
            progress.working_on(step)
            progress.advance()
    return seen


def test_bar_counts_steps_on_a_terminal(terminal):
    progress = run(["imgui", "implot", "assembling outputs"])
    task = progress.progress.tasks[0]
    assert (task.completed, task.total) == (3, 3)
    assert task.description == "assembling outputs"


def test_printed_lines_survive_the_bar(terminal):
    with RunProgress(1) as progress:
        rich.print("[bold green]Created[/bold green]: src/a_auto.cpp")
        progress.advance()
    plain = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", terminal.getvalue())  # drop the colour codes
    assert "Created: src/a_auto.cpp" in plain


def test_nothing_is_drawn_off_a_terminal(monkeypatch):
    out = io.StringIO()
    monkeypatch.setattr(rich, "_console", Console(file=out, force_terminal=False))
    progress = run(["imgui"])
    assert progress.progress is None
    assert out.getvalue() == ""


def test_task_name():
    assert task_name(SimpleNamespace(unit=SimpleNamespace(name="imgui"))) == "imgui"
    assert task_name(object()) == "object"
