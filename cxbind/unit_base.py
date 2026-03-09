from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .spec import EntryKey, EntryKeySet, SpecMap


class UnitBase(BaseModel):
    name: str | None = None
    module: str | None = None
    flags: list[str] | None = None
    prefixes: list[str] = Field(default_factory=list)
    defaults: dict[str, Any] = Field(default_factory=dict)
    specs: SpecMap = Field(default_factory=SpecMap)
    excludes: EntryKeySet = Field(default_factory=set)
    tool: str | None = None

    model_config = ConfigDict(extra="forbid")