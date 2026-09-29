"""Per-run Markdown report: <project>/_cxbind/cxbind_report.md.

The log (_cxbind/cxbind.log) has everything, line by line, for grep. The
report has what a person should look at after a run:

  - outputs: every generated file, per unit and target kind, with its status
    (unchanged, changed, new, orphaned) and, for changes, the diff;
  - warnings: everything logged at WARNING or above, grouped by where it
    came from, repeats collapsed;
  - per-unit tables backends contribute (e.g. node kinds without a stub
    renderer, C++ types that became Any).

Backends add to the current report with Report.current(); code running
outside a cxbind run (no current report) simply skips reporting.
"""

from __future__ import annotations

import html
import os
import re
import time
from collections import Counter
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from loguru import logger

REPORT_NAME = "cxbind_report.md"

STATUS_ICONS = {"unchanged": "✅", "changed": "✏️", "new": "🆕", "orphaned": "🗑️", "written": "📝"}

_current: ContextVar["Report | None"] = ContextVar("cxbind_report", default=None)


@dataclass
class Output:
    unit: str
    kind: str
    path: Path  # relative to the project directory
    status: str = "written"  # unchanged | changed | new | orphaned; "written" if not compared
    diff: str = ""


@dataclass
class Table:
    unit: str
    title: str
    headers: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class LogWarning:
    level: str
    module: str
    function: str
    line: int
    message: str


@dataclass
class Report:
    project_dir: Path
    title: str
    check: bool = False  # a --check run: outputs describe what *would* change
    outputs: list[Output] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    warnings: list[LogWarning] = field(default_factory=list)
    error: str | None = None

    # --- lifecycle -------------------------------------------------------

    @classmethod
    def current(cls) -> "Report | None":
        return _current.get()

    @contextmanager
    def active(self) -> Generator["Report", None, None]:
        """Make this the current report and collect WARNING+ log records."""
        self.started = datetime.now()
        start = time.monotonic()
        token = _current.set(self)
        sink = logger.add(self._collect, level="WARNING", format="{message}")
        try:
            yield self
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            raise
        finally:
            logger.remove(sink)
            _current.reset(token)
            self.elapsed = time.monotonic() - start

    def _collect(self, message) -> None:
        r = message.record
        self.warnings.append(
            LogWarning(r["level"].name, r["name"] or "?", r["function"], r["line"], str(r["message"]))
        )

    # --- contributions ---------------------------------------------------

    def output(self, unit: str, kind: str, path: Path | str, status: str = "written", diff: str = "") -> None:
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(self.project_dir.resolve())
        self.outputs.append(Output(unit, kind, path, status, diff))

    def table(self, unit: str, title: str, headers: list[str], rows: list[list[object]]) -> None:
        if rows:
            self.tables.append(Table(unit, title, headers, [[str(c) for c in r] for r in rows]))

    # --- rendering -------------------------------------------------------

    @property
    def out_of_date(self) -> list[Output]:
        return [o for o in self.outputs if o.status in ("changed", "new", "orphaned")]

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(path.parent))

    def render(self, base: Path) -> str:
        if self.error:
            status = "❌ failed"
        elif self.check and self.out_of_date:
            status = "❌ out of date"
        elif self.warnings:
            status = "⚠️ warnings"
        else:
            status = "✅ ok"
        mode = " (check)" if self.check else ""
        out = [
            f"# cxbind — {self.title}{mode} — {status}\n",
            f"_{self.started:%Y-%m-%d %H:%M:%S} · {self.elapsed:.1f}s · "
            f"{self.render_counts()} · {len(self.warnings)} warning(s)_\n",
        ]
        if self.error:
            out.append(f"## Error\n\n```text\n{self.error}\n```\n")
        out.append(self.render_outputs(base))
        out.append(self.render_changes())
        out.append(self.render_warnings())
        out.append(self.render_units())
        return "\n".join(part for part in out if part)

    def render_counts(self) -> str:
        if not self.outputs:
            return "0 outputs"
        counts = Counter(o.status for o in self.outputs)
        order = ["changed", "new", "orphaned", "unchanged", "written"]
        detail = ", ".join(f"{counts[s]} {s}" for s in order if counts[s])
        return f"{len(self.outputs)} output(s): {detail}"

    def link(self, rel: Path, base: Path) -> str:
        target = (self.project_dir / rel).resolve()
        return Path(os.path.relpath(target, base.resolve())).as_posix()

    def render_outputs(self, base: Path) -> str:
        if not self.outputs:
            return "## Outputs\n\nNothing was generated.\n"
        rows = ["## Outputs\n", "| Status | Unit | Kind | File |", "|--------|------|------|------|"]
        for o in self.outputs:
            name = o.path.as_posix()
            exists = (self.project_dir / o.path).exists()
            file = f"[{name}]({self.link(o.path, base)})" if exists else f"`{name}`"
            icon = STATUS_ICONS.get(o.status, "")
            rows.append(f"| {icon} {o.status} | {cell(o.unit)} | {o.kind} | {file} |")
        return "\n".join(rows) + "\n"

    def render_changes(self) -> str:
        changed = [o for o in self.out_of_date if o.diff]
        if not changed:
            return ""
        verb = "What would change" if self.check else "What changed"
        out = [f"## {verb}\n", "Review with `git diff`; accept by committing, reject with `git restore`.\n"]
        for o in changed:
            is_note = o.diff.startswith("(")  # new or orphaned files: a size note, not a diff
            body = o.diff if o.diff.endswith("\n") else o.diff + "\n"
            fence = fence_for(body)
            lang = "text" if is_note else "diff"
            summary = html.escape(f"{o.status}: {o.path.as_posix()}")
            out += [
                f"<details{'' if is_note else ' open'}>\n<summary>{summary}</summary>\n",
                f"{fence}{lang}\n{body}{fence}\n",
                "</details>\n",
            ]
        return "\n".join(out)

    def render_warnings(self) -> str:
        if not self.warnings:
            return ""
        counts = Counter(self.warnings)
        by_module: dict[str, list[LogWarning]] = {}
        for w in counts:  # first occurrence order, repeats collapsed
            by_module.setdefault(w.module, []).append(w)

        out = [f"## Warnings ({len(self.warnings)})\n"]
        for module, items in by_module.items():
            out.append(f"### `{module}`\n")
            for w in items:
                times = f" ×{counts[w]}" if counts[w] > 1 else ""
                first, _, rest = w.message.partition("\n")
                out.append(f"- **{w.level}** `{w.function}:{w.line}`{times}: {first}")
                if rest:
                    out.append(f"\n  ```text\n{indent(rest)}\n  ```")
            out.append("")
        return "\n".join(out)

    def render_units(self) -> str:
        if not self.tables:
            return ""
        out = ["## Units\n"]
        units = list(dict.fromkeys(t.unit for t in self.tables))
        for unit in units:
            out.append(f"### {unit}\n")
            for t in (t for t in self.tables if t.unit == unit):
                out.append(f"#### {t.title}\n")
                out.append("| " + " | ".join(t.headers) + " |")
                out.append("|" + "|".join("---" for _ in t.headers) + "|")
                for row in t.rows:
                    out.append("| " + " | ".join(cell(c) for c in row) + " |")
                out.append("")
        return "\n".join(out)


def cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def indent(text: str) -> str:
    return "\n".join(f"  {line}" for line in text.splitlines())


def fence_for(text: str) -> str:
    """A code fence longer than any backtick run inside `text`."""
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)
