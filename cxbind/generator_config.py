from typing import List, Optional

from pydantic import BaseModel

from .entry import Entry, FunctionEntry, StructEntry, FieldEntry

class GeneratorConfig(BaseModel):
    """Generator configuration."""
    source: str
    target: str
    module: str
    prefixes: Optional[str | List[str]] = None
    flags: List[str]
    #
    function: Optional[List[FunctionEntry]] = []
    struct: Optional[List[StructEntry]] = []
    field: Optional[List[FieldEntry]] = []