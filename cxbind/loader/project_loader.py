from typing import List, Optional
from pathlib import Path

from loguru import logger

from collections import defaultdict
from pydantic import ValidationError

from .unit_base_loader import UnitBaseLoader

from ..project import Project


def explain(e: ValidationError) -> None:
    groups = defaultdict(list)
    for err in e.errors(include_url=False):
        loc = []
        for p in err["loc"]:
            # shorten noisy dict keys
            loc.append(getattr(p, "name", None) or str(p))
        groups[(err["type"], err["msg"], err["loc"][-1])].append((".".join(loc), err["input"]))

    for (typ, msg, field), hits in groups.items():
        print(f"[{typ}] {msg}: '{field}' ({len(hits)}x)")
        for path, inp in hits:
            print(f"    at {path}")
            print(f"       got {inp!r}")


class ProjectLoader(UnitBaseLoader):
    def __init__(self) -> None:
        self.project: Optional[Project] = None

    def load(self, path: Path) -> Project:
        data = self.load_yaml(path)

        # Validate with Pydantic
        try:
            self.project = project = Project.model_validate(data)
        except ValidationError as e:
            logger.error(f"Failed to validate project data:")
            explain(e)
            raise

        project.path = path

        if project.name is None:
            project.name = path.stem

        return project
