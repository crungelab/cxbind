from ..project import Project
from ..unit import Unit
from ..target import merge_targets


class UnitConfigurator:
    def __init__(self, project: Project, unit: Unit) -> None:
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

        if unit.flags is None:
            if project.flags is not None:
                unit.flags = project.flags
            else:
                raise ValueError("flags are required")

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