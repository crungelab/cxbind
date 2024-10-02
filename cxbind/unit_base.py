from typing import List, Dict, Optional

from pydantic import BaseModel, Field

from .node import NodeUnion, NodeDict

class UnitBase(BaseModel):
    name: Optional[str] = None
    module: Optional[str] = None
    flags: Optional[List[str]] = None
    prefixes: Optional[List[str]] = []
    defaults: Optional[dict] = {}
    #nodes: Optional[dict[str, NodeUnion]] = {}
    nodes: Optional[NodeDict] = {}
