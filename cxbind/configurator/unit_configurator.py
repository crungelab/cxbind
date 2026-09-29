from pathlib import Path
import sysconfig

from loguru import logger

import cxbind

from ..project import Project
from ..unit import Unit
from ..target import merge_targets


# Python.h for the interpreter cxbind runs on: the one the bindings are built for.
PYTHON_INCLUDE = sysconfig.get_paths()["include"]

# cxbind's own headers (cxbind/cxbind.h), wherever cxbind is installed:
# the package directory in a checkout (editable) or in site-packages.
CXBIND_INCLUDE = Path(cxbind.__file__).parent / "include"

# cxbind only parses headers, so the language picks the header flavour.
LANGUAGES = {"c": "c-header", "c++": "c++-header"}


def resolve_flags(unit: Unit, project: Project) -> None:
    """A unit's final clang flags: its own (or the project's), led by -x for its language.

    Call once per unit, when the project is loaded.
    """
    logger.debug(f"Unit {unit.name} language: {unit.language}")
    logger.debug(f"Project {project.name} language: {project.language}")

    flags = list(unit.flags if unit.flags is not None else project.flags or [])

    language = unit.language if unit.language is not None else project.language
    if language is None:
        raise ValueError(f"unit {unit.name}: language is required: set `language: c` or `language: c++` in the project or the unit")
    if language not in LANGUAGES:
        raise ValueError(f"unit {unit.name}: unknown language {language!r} (use c or c++)")
    if any(flag.startswith("-x") for flag in flags):
        raise ValueError(
            f"unit {unit.name}: flags set the language with -x; "
            f"remove it and use `language: {language}` instead"
        )

    #unit.flags = ["-x", LANGUAGES[language], *flags]
    unit.flags = ["-x", LANGUAGES[language], *flags, f"-I{CXBIND_INCLUDE}", f"-I{PYTHON_INCLUDE}"]
    logger.debug(f"Unit flags: {unit.flags}")

class UnitConfigurator:
    def __init__(self, unit: Unit, project: Project) -> None:
        self.project = project
        self.unit = unit

    def configure(self):
        project = self.project
        unit = self.unit

        if unit.module is None:
            if project.module is not None:
                unit.module = project.module
            else:
                raise ValueError("module is required")

        resolve_flags(unit, project)

        '''
        if unit.flags is None:
            if project.flags is not None:
                unit.flags = project.flags
            else:
                raise ValueError("flags are required")
        '''

        # Order needs to be from specific to generic.  Example: prefixes: [SDL_EVENT_, SDL_]
        unit.prefixes = unit.prefixes + project.prefixes

        unit.specs = {**project.specs, **unit.specs}

        # Unit targets override project targets per kind; null removes one.
        # Must come after module is resolved: paths may use {module}.
        unit.targets = merge_targets(
            project.targets,
            unit.targets,
            name=unit.name,
            module=unit.module,
        )