"""Per-run Markdown report: <project>/_cxbind/report.md.

The log (_cxbind/cxbind.log) has everything, line by line, for grep. The
report has what a person should look at after a run:

  - outputs: every file written, per unit and target kind, as links;
  - warnings: everything logged at WARNING or above, grouped by where it
    came from, repeats collapsed;
  - per-unit tables backends contribute (e.g. node kinds without a stub
    renderer, C++ types that became Any).

Backends add to the current report with Report.current(); code running
outside a cxbind run (no current report) simply skips reporting.
"""

from __future__ import annotations

import os
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

_current: ContextVar["Report | None"] = ContextVar("cxbind_report", default=None)


@dataclass
class Output:
    unit: str
    kind: str
    path: Path  # relative to the project directory


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

    def output(self, unit: str, kind: str, path: Path | str) -> None:
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(self.project_dir.resolve())
        self.outputs.append(Output(unit, kind, path))

    def table(self, unit: str, title: str, headers: list[str], rows: list[list[object]]) -> None:
        if rows:
            self.tables.append(Table(unit, title, headers, [[str(c) for c in r] for r in rows]))

    # --- rendering -------------------------------------------------------

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(path.parent))

    def render(self, base: Path) -> str:
        status = "❌ failed" if self.error else ("⚠️ warnings" if self.warnings else "✅ ok")
        out = [
            f"# cxbind — {self.title} — {status}\n",
            f"_{self.started:%Y-%m-%d %H:%M:%S} · {self.elapsed:.1f}s · "
            f"{len(self.outputs)} output(s) · {len(self.warnings)} warning(s)_\n",
        ]
        if self.error:
            out.append(f"## Error\n\n```text\n{self.error}\n```\n")
        out.append(self.render_outputs(base))
        out.append(self.render_warnings())
        out.append(self.render_units())
        return "\n".join(part for part in out if part)

    def link(self, rel: Path, base: Path) -> str:
        target = (self.project_dir / rel).resolve()
        return Path(os.path.relpath(target, base.resolve())).as_posix()

    def render_outputs(self, base: Path) -> str:
        if not self.outputs:
            return "## Outputs\n\nNothing was written.\n"
        rows = ["## Outputs\n", "| Unit | Kind | File |", "|------|------|------|"]
        for o in self.outputs:
            rows.append(f"| {o.unit} | {o.kind} | [{o.path.as_posix()}]({self.link(o.path, base)}) |")
        return "\n".join(rows) + "\n"

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