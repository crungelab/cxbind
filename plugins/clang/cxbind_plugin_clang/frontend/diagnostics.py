"""Turning libclang diagnostics into log lines, and parse errors into one clear failure."""

from __future__ import annotations

from clang import cindex
from loguru import logger

from cxbind.cxbind import CxBindError

MAX_SHOWN = 5  # errors quoted in the failure message; the log has them all

LOG_LEVELS = {
    cindex.Diagnostic.Ignored: "DEBUG",
    cindex.Diagnostic.Note: "DEBUG",
    cindex.Diagnostic.Warning: "WARNING",
    cindex.Diagnostic.Error: "ERROR",
    cindex.Diagnostic.Fatal: "ERROR",
}


class ParseError(CxBindError):
    """libclang reported errors: the parse is incomplete, so nothing may be generated from it."""


def include_chain(tu: cindex.TranslationUnit, file_name: str) -> list[str]:
    """Where `file_name` was included from, innermost first: ['src/unit.h:2', ...]."""
    parents: dict[str, tuple[str, int]] = {}
    for inclusion in tu.get_includes():
        parents.setdefault(inclusion.include.name, (inclusion.source.name, inclusion.location.line))
    chain, seen = [], set()
    while file_name in parents and file_name not in seen:
        seen.add(file_name)
        file_name, line = parents[file_name]
        chain.append(f"{file_name}:{line}")
    return chain


def describe(tu: cindex.TranslationUnit, diag: cindex.Diagnostic) -> str:
    """'file:line:col: message', plus how that file got into the parse."""
    loc = diag.location
    where = f"{loc.file.name}:{loc.line}:{loc.column}" if loc.file else "<command line>"
    text = f"{where}: {diag.spelling}"
    if loc.file and (chain := include_chain(tu, loc.file.name)):
        text += " (included from " + ", from ".join(chain) + ")"
    return text


def check_diagnostics(tu: cindex.TranslationUnit, unit: str, path: object, flags: list[str]) -> None:
    """Log every diagnostic at its severity; raise ParseError if any was an error."""
    errors = []
    for diag in tu.diagnostics:
        text = describe(tu, diag)
        logger.log(LOG_LEVELS.get(diag.severity, "WARNING"), f"{unit}: {text}")
        if diag.severity >= cindex.Diagnostic.Error:
            errors.append((diag, text))
    if not errors:
        return

    language = next((flags[i + 1] for i, f in enumerate(flags[:-1]) if f == "-x"), "by file extension")
    lines = [f"{unit}: {len(errors)} error(s) parsing {path} (as {language}); nothing was generated from it."]
    lines += [f"  {text}" for _, text in errors[:MAX_SHOWN]]
    if len(errors) > MAX_SHOWN:
        lines.append(f"  ... and {len(errors) - MAX_SHOWN} more in the log")
    if any("file not found" in diag.spelling for diag, _ in errors):
        searched = [f for f in flags if f.startswith(("-I", "-isystem", "-iquote"))] or ["(none)"]
        lines.append("  A header wasn't found. Include paths given: " + " ".join(searched))
    raise ParseError("\n".join(lines))