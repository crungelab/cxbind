from typing import List, Optional

from pydantic import BaseModel


class UnitBase(BaseModel):
    name: Optional[str] = None
    module: Optional[str] = None
    flags: Optional[List[str]] = None
    prefixes: Optional[List[str]] = []
    defaults: Optional[dict] = {}
