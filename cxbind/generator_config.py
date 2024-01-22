from typing import List, Optional

from pydantic import BaseModel, Field

from .entry import FunctionEntry, MethodEntry, StructEntry, ClassEntry, FieldEntry

class GeneratorConfig(BaseModel):
    """Generator configuration."""
    source: str
    target: str
    module: str
    prefixes: Optional[str | List[str]] = []
    flags: List[str]
    defaults: Optional[dict] = {}
    #
    function: Optional[List[FunctionEntry]] = []
    method: Optional[List[MethodEntry]] = []
    struct: Optional[List[StructEntry]] = []
    cls: Optional[List[ClassEntry]] = Field([], alias='class')
    field: Optional[List[FieldEntry]] = []