from typing import List, Optional

from pydantic import BaseModel


class UnitBase(BaseModel):
    #source: str
    #target: str
    #module: str
    name: Optional[str] = None
    module: Optional[str] = None
    prefixes: Optional[str | List[str]] = []
    #flags: List[str]
    flags: Optional[List[str]] = None
    defaults: Optional[dict] = {}
    #
    #function: Optional[List[FunctionNode]] = []
    #method: Optional[List[MethodNode]] = []
    #struct: Optional[List[StructNode]] = []
    #cls: Optional[List[ClassNode]] = Field([], alias='class')
    #field: Optional[List[FieldNode]] = []
    #ctor: Optional[List[CtorNode]] = []