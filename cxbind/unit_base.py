from typing import List, Dict, Optional

from pydantic import BaseModel, Field

from .spec import SpecDict

class UnitBase(BaseModel):
    name: Optional[str] = None
    module: Optional[str] = None
    flags: Optional[List[str]] = None
    prefixes: Optional[List[str]] = []
    defaults: Optional[dict] = {}
    specs: Optional[SpecDict] = {}
    excludes: Optional[List[str]] = []
    program: Optional[str] = None