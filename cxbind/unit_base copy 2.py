from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, field_validator

from .spec import SpecDict, EntryKey

class UnitBase(BaseModel):
    name: Optional[str] = None
    module: Optional[str] = None
    flags: Optional[List[str]] = None
    prefixes: Optional[List[str]] = []
    defaults: Optional[dict] = {}
    specs: Optional[SpecDict] = {}
    #excludes: Optional[List[str]] = []
    excludes: Optional[List[EntryKey]] = []
    tool: Optional[str] = None

    @field_validator("excludes", mode="before")
    @classmethod
    def _parse_excludes(cls, v: Any):
        if v is None:
            return []

        out = []

        for item in v:
            if isinstance(item, EntryKey):
                out.append(item)
            elif isinstance(item, str):
                out.append(EntryKey.parse(item))
            else:
                raise TypeError(f"Invalid exclude entry: {item!r}")

        return out