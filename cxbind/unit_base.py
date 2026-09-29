from __future__ import annotations

from typing import Any
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .spec import EntryKey, EntryKeySet, SpecMap
from .target import Target, dispatch_targets


class UnitBase(BaseModel):
    name: str | None = None
    module: str | None = None
    language: str | None = None   # None: use the project's
    flags: list[str] | None = None
    prefixes: list[str] = Field(default_factory=list)
    defaults: dict[str, Any] = Field(default_factory=dict)
    specs: SpecMap = Field(default_factory=SpecMap)
    excludes: EntryKeySet = Field(default_factory=set)
    tool: str | None = None
    targets: dict[str, Target | None] = Field(default_factory=dict)
    path: Path = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(extra="forbid")

    @field_validator("targets", mode="before")
    @classmethod
    def validate_targets(cls, v):
        return dispatch_targets(v)

    @property
    def config_subdir(self) -> Path | None:
        """Where this definition's file sits inside its .cxbind directory.

        `.cxbind/effects/x.unit.yaml` -> `effects`; a file directly in .cxbind
        -> `.` (no parts); None if not loaded from a file inside a .cxbind.
        """
        if self.path is None:
            return None
        file = self.path.resolve()
        for ancestor in file.parents:
            if ancestor.name == ".cxbind":
                return file.parent.relative_to(ancestor)
        return None