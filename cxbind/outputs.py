"""Writing generated files: every output of a cxbind run goes through write_output().

Generated files are committed, so the files on disk are the snapshots. Each output
is compared with the file already there before anything is written:

  - unchanged: left alone, so its timestamp stays and the build doesn't recompile it;
  - changed or new: written, with a git-style diff recorded for the report.

Review changes with `git diff`; accept them by committing, reject them with
`git restore`. In check mode (`cxbind --check`) nothing is written at all: the run
only reports what would change, and the CLI fails if anything would.

When a run generates every unit, files the previous run generated (per the manifest)
that this run didn't are orphans: deleted in a normal run, reported in check mode.
A run of a single unit can't tell another unit's files from orphans, so it leaves
them, and the manifest's other entries, alone.
"""

from __future__ import annotations

import difflib
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from loguru import logger
from rich import print

from .manifest import Manifest
from .report import Report

# Diffs beyond this many lines are cut short in the report: git diff has the rest.
DIFF_LINE_LIMIT = 2000


class Status(str, Enum):
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    NEW = "new"
    ORPHANED = "orphaned"


@dataclass
class Change:
    unit: str
    kind: str
    path: Path  # relative to the project directory
    status: Status
    diff: str = ""


_current: ContextVar["Outputs | None"] = ContextVar("cxbind_outputs", default=None)


@dataclass
class Outputs:
    project_dir: Path
    manifest: Manifest
    check: bool = False  # write nothing; only report what would change
    complete: bool = True  # every unit is being generated: orphans can be recognized
    previous: list[Path] = field(default_factory=list)  # relative: what the last run generated
    changes: list[Change] = field(default_factory=list)

    @classmethod
    def current(cls) -> "Outputs | None":
        return _current.get()

    @property
    def out_of_date(self) -> list[Change]:
        """Everything a normal run changed, or a check run would have."""
        return [c for c in self.changes if c.status is not Status.UNCHANGED]

    @contextmanager
    def active(self) -> Generator["Outputs", None, None]:
        """Make this the run's outputs. Reads the previous manifest before anything changes it."""
        base = self.manifest.project_dir
        self.previous = [p.relative_to(base) for p in self.manifest.outputs()]
        if self.complete and not self.check:
            self.manifest.reset()
        token = _current.set(self)
        try:
            yield self
        finally:
            _current.reset(token)

    # --- writing ---------------------------------------------------------

    def write(self, unit: str, kind: str, path: Path | str, text: str) -> Change:
        if not text.endswith("\n"):
            text += "\n"
        absolute = Path(path) if Path(path).is_absolute() else self.project_dir / path
        relative = absolute.resolve().relative_to(self.project_dir.resolve())
        # read_text normalizes line endings, so a CRLF checkout of an unchanged file compares equal.
        old = absolute.read_text(encoding="utf-8") if absolute.is_file() else None

        if old == text:
            status, diff = Status.UNCHANGED, ""
        elif old is None:
            status, diff = Status.NEW, _new_file_note(text)
        else:
            status, diff = Status.CHANGED, _diff(old, text, relative)

        if not self.check:
            if status is not Status.UNCHANGED:
                absolute.parent.mkdir(parents=True, exist_ok=True)
                absolute.write_text(text, encoding="utf-8")
            self.manifest.record(absolute)

        change = Change(unit, kind, relative, status, diff)
        self.changes.append(change)
        self._announce(change)
        if (report := Report.current()) is not None:
            report.output(unit, kind, relative, status.value, diff)
        return change

    def finish(self) -> None:
        """Deal with orphans: files the previous run generated and this complete run didn't."""
        if not self.complete:
            return
        written = {c.path for c in self.changes}
        if not self.check:
            # Also everything recorded in the manifest during this run, whichever code path
            # wrote it: a file generated without going through write_output is not an orphan.
            base = self.manifest.project_dir
            recorded = {p.relative_to(base) for p in self.manifest.outputs()}
            if recorded and not self.changes:
                # Files were generated, but none through write_output: some writer still
                # bypasses it, so this run can't tell orphans apart safely. Remove nothing.
                logger.warning(
                    "generated files were recorded without going through write_output; "
                    "skipping orphan removal (convert every writer to write_output)"
                )
                return
            written |= recorded
        for relative in self.previous:
            absolute = self.project_dir / relative
            if relative in written or not absolute.is_file():
                continue
            lines = len(absolute.read_text(encoding="utf-8", errors="replace").splitlines())
            diff = f"(no longer generated: {lines} lines)"
            if not self.check:
                absolute.unlink()
                logger.info(f"removed {relative}: no longer generated")
            change = Change("-", "orphan", relative, Status.ORPHANED, diff)
            self.changes.append(change)
            self._announce(change)
            if (report := Report.current()) is not None:
                report.output("-", "orphan", relative, Status.ORPHANED.value, diff)

    def _announce(self, change: Change) -> None:
        verbs = {
            Status.UNCHANGED: ("dim", "Unchanged", "Unchanged"),
            Status.CHANGED: ("bold yellow", "Updated", "Would update"),
            Status.NEW: ("bold green", "Created", "Would create"),
            Status.ORPHANED: ("bold red", "Removed", "Would remove"),
        }
        style, done, would = verbs[change.status]
        print(f"[{style}]{would if self.check else done}[/{style}]: {change.path.as_posix()}")


def write_output(unit: str, kind: str, path: Path | str, text: str) -> Change | None:
    """Write one generated file through the current run's Outputs.

    Outside a cxbind run (a backend used directly, say) it simply writes the file.
    """
    outputs = Outputs.current()
    if outputs is None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        return None
    return outputs.write(unit, kind, path, text)


def _diff(old: str, new: str, relative: Path) -> str:
    name = relative.as_posix()
    lines = list(
        difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True), f"a/{name}", f"b/{name}"
        )
    )
    if len(lines) > DIFF_LINE_LIMIT:
        cut = len(lines) - DIFF_LINE_LIMIT
        lines = lines[:DIFF_LINE_LIMIT] + [f"\n... {cut} more diff lines: see `git diff -- {name}`\n"]
    return "".join(lines)


def _new_file_note(text: str) -> str:
    # A new file's "diff" is the whole file, which can be huge (skia): just say how big.
    return f"(new file: {len(text.splitlines())} lines)"
