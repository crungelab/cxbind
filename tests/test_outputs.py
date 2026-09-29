"""cxbind.outputs: comparing generated files with the committed ones, and check mode."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from cxbind.manifest import Manifest
from cxbind.outputs import Outputs, Status, write_output
from cxbind.report import Report


@pytest.fixture
def project(tmp_path) -> Path:
    return tmp_path


def run(project: Path, files: dict[str, str], *, check: bool = False, complete: bool = True,
        report: Report | None = None) -> Outputs:
    """One cxbind run that generates `files` ({path: text}), through write_output like the backends."""
    outputs = Outputs(project, Manifest(project / "_cxbind"), check=check, complete=complete)
    with outputs.active():
        if report is not None:
            with report.active():
                for path, text in files.items():
                    write_output("unit", "pybind11", path, text)
                outputs.finish()
        else:
            for path, text in files.items():
                write_output("unit", "pybind11", path, text)
            outputs.finish()
    return outputs


def statuses(outputs: Outputs) -> dict[str, Status]:
    return {c.path.as_posix(): c.status for c in outputs.changes}


def recorded(project: Path) -> list[str]:
    return [p.relative_to(project).as_posix() for p in Manifest(project / "_cxbind").outputs()]


def test_new_files_are_written_and_recorded(project):
    outputs = run(project, {"src/a_auto.cpp": "int a;\n"})
    assert statuses(outputs) == {"src/a_auto.cpp": Status.NEW}
    assert (project / "src/a_auto.cpp").read_text() == "int a;\n"
    assert recorded(project) == ["src/a_auto.cpp"]


def test_unchanged_files_keep_their_timestamp(project):
    run(project, {"src/a_auto.cpp": "int a;\n"})
    path = project / "src/a_auto.cpp"
    os.utime(path, (1_000_000_000, 1_000_000_000))
    outputs = run(project, {"src/a_auto.cpp": "int a;\n"})
    assert statuses(outputs) == {"src/a_auto.cpp": Status.UNCHANGED}
    assert path.stat().st_mtime == 1_000_000_000  # not rewritten: the build won't recompile it
    assert outputs.out_of_date == []


def test_changed_files_are_written_with_a_diff(project):
    run(project, {"src/a_auto.cpp": "int a;\nint b;\n"})
    outputs = run(project, {"src/a_auto.cpp": "int a;\nint c;\n"})
    [change] = outputs.changes
    assert change.status is Status.CHANGED
    assert "--- a/src/a_auto.cpp" in change.diff and "+++ b/src/a_auto.cpp" in change.diff
    assert "-int b;" in change.diff and "+int c;" in change.diff
    assert (project / "src/a_auto.cpp").read_text() == "int a;\nint c;\n"


def test_check_mode_writes_nothing(project):
    run(project, {"src/a_auto.cpp": "int a;\n", "src/gone.cpp": "old\n"})
    before = {p: p.read_text() for p in project.rglob("*") if p.is_file()}
    outputs = run(project, {"src/a_auto.cpp": "int a2;\n", "src/new.cpp": "new\n"}, check=True)
    assert statuses(outputs) == {
        "src/a_auto.cpp": Status.CHANGED,
        "src/new.cpp": Status.NEW,
        "src/gone.cpp": Status.ORPHANED,
    }
    assert {p: p.read_text() for p in project.rglob("*") if p.is_file()} == before  # files and manifest alike
    assert len(outputs.out_of_date) == 3


def test_orphans_are_removed_in_a_complete_run(project):
    run(project, {"src/a_auto.cpp": "a\n", "src/old_auto.cpp": "old\n"})
    outputs = run(project, {"src/a_auto.cpp": "a\n"})
    assert statuses(outputs)["src/old_auto.cpp"] is Status.ORPHANED
    assert not (project / "src/old_auto.cpp").exists()
    assert recorded(project) == ["src/a_auto.cpp"]


def test_a_single_unit_run_leaves_other_units_alone(project):
    run(project, {"src/a_auto.cpp": "a\n", "src/b_auto.cpp": "b\n"})
    outputs = run(project, {"src/a_auto.cpp": "a2\n"}, complete=False)
    assert statuses(outputs) == {"src/a_auto.cpp": Status.CHANGED}
    assert (project / "src/b_auto.cpp").exists()  # not an orphan: just not generated this time
    assert set(recorded(project)) == {"src/a_auto.cpp", "src/b_auto.cpp"}


def test_orphans_are_only_files_the_manifest_lists(project):
    (project / "src/hand_written.cpp").parent.mkdir(parents=True)
    (project / "src/hand_written.cpp").write_text("mine\n")
    run(project, {"src/a_auto.cpp": "a\n"})
    run(project, {"src/a_auto.cpp": "a\n"})
    assert (project / "src/hand_written.cpp").read_text() == "mine\n"


def test_crlf_line_endings_on_disk_compare_equal(project):
    path = project / "src/a_auto.cpp"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"int a;\r\nint b;\r\n")  # a Windows checkout of a committed file
    outputs = run(project, {"src/a_auto.cpp": "int a;\nint b;\n"})
    assert statuses(outputs) == {"src/a_auto.cpp": Status.UNCHANGED}


def test_a_missing_final_newline_is_added(project):
    run(project, {"src/a.pyi": "x: int"})
    assert (project / "src/a.pyi").read_text() == "x: int\n"


def test_huge_diffs_are_cut_short(project, monkeypatch):
    import cxbind.outputs as outputs_module

    monkeypatch.setattr(outputs_module, "DIFF_LINE_LIMIT", 10)
    run(project, {"big.cpp": "".join(f"line {i}\n" for i in range(100))})
    outputs = run(project, {"big.cpp": "".join(f"LINE {i}\n" for i in range(100))})
    assert "more diff lines: see `git diff -- big.cpp`" in outputs.changes[0].diff


def test_outside_a_run_write_output_just_writes(project):
    assert write_output("unit", "pyi", project / "x.pyi", "y: int") is None
    assert (project / "x.pyi").read_text() == "y: int\n"


# --- the report -------------------------------------------------------------------


def test_report_shows_statuses_and_diffs(project):
    run(project, {"src/a_auto.cpp": "int a;\n", "src/b_auto.cpp": "int b;\n", "src/old.cpp": "o\n"})
    report = Report(project, "imgui")
    run(project, {"src/a_auto.cpp": "int a;\n", "src/b_auto.cpp": "int B;\n", "src/new.cpp": "n\n"}, report=report)
    text = report.render(project / "_cxbind")
    assert text.startswith("# cxbind — imgui — ✅ ok")
    assert "4 output(s): 1 changed, 1 new, 1 orphaned, 1 unchanged" in text
    assert "| ✏️ changed | unit | pybind11 | [src/b_auto.cpp](../src/b_auto.cpp) |" in text
    assert "| 🗑️ orphaned | - | orphan | `src/old.cpp` |" in text  # gone: no dead link
    assert "## What changed" in text and "+int B;" in text
    assert "(new file: 1 lines)" in text


def test_report_in_check_mode_says_out_of_date(project):
    run(project, {"src/a_auto.cpp": "int a;\n"})
    report = Report(project, "imgui", check=True)
    run(project, {"src/a_auto.cpp": "int A;\n"}, check=True, report=report)
    text = report.render(project / "_cxbind")
    assert text.startswith("# cxbind — imgui (check) — ❌ out of date")
    assert "## What would change" in text


def test_report_in_check_mode_is_ok_when_nothing_changes(project):
    run(project, {"src/a_auto.cpp": "int a;\n"})
    report = Report(project, "imgui", check=True)
    run(project, {"src/a_auto.cpp": "int a;\n"}, check=True, report=report)
    assert report.render(project / "_cxbind").startswith("# cxbind — imgui (check) — ✅ ok")


def test_files_written_outside_write_output_are_not_orphans(project):
    """A writer not yet converted to write_output (it writes and records the file itself)
    must never have its fresh output deleted as an orphan."""
    run(project, {"src/a_auto.cpp": "a\n"})
    outputs = Outputs(project, Manifest(project / "_cxbind"))
    with outputs.active():
        path = project / "src" / "a_auto.cpp"
        path.write_text("a2\n")  # the old Backend.write, in effect
        Manifest(project / "_cxbind").record(path)
        outputs.finish()
    assert path.read_text() == "a2\n"
    assert not [c for c in outputs.changes if c.status is Status.ORPHANED]


def test_a_mix_of_old_and_new_writers_still_finds_real_orphans(project):
    run(project, {"src/a_auto.cpp": "a\n", "src/b_auto.cpp": "b\n", "src/gone.cpp": "g\n"})
    outputs = Outputs(project, Manifest(project / "_cxbind"))
    with outputs.active():
        write_output("unit", "pybind11", "src/a_auto.cpp", "a\n")  # a converted writer
        b = project / "src" / "b_auto.cpp"
        b.write_text("b\n")  # an old one
        Manifest(project / "_cxbind").record(b)
        outputs.finish()
    assert b.exists()
    assert not (project / "src/gone.cpp").exists()  # a genuine orphan is still removed
