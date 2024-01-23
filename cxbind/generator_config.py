from typing import List, Optional

from pydantic import BaseModel, Field

from .node import FunctionNode, MethodNode, StructNode, ClassNode, FieldNode

class GeneratorConfig(BaseModel):
    """Generator configuration."""
    source: str
    target: str
    module: str
    prefixes: Optional[str | List[str]] = []
    flags: List[str]
    defaults: Optional[dict] = {}
    #
    function: Optional[List[FunctionNode]] = []
    method: Optional[List[MethodNode]] = []
    struct: Optional[List[StructNode]] = []
    cls: Optional[List[ClassNode]] = Field([], alias='class')
    field: Optional[List[FieldNode]] = []