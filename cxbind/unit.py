from typing import List, Optional
from pathlib import Path

from loguru import logger
import yaml
from pydantic import Field

from .node import FunctionNode, MethodNode, StructNode, ClassNode, FieldNode, CtorNode
from .unit_base import UnitBase

class Unit(UnitBase):
    source: str
    target: str

    struct: Optional[List[StructNode]] = []
    cls: Optional[List[ClassNode]] = Field([], alias='class')
    field: Optional[List[FieldNode]] = []

    function: Optional[List[FunctionNode]] = []
    method: Optional[List[MethodNode]] = []
    ctor: Optional[List[CtorNode]] = []
