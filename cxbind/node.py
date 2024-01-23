from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field

from clang import cindex
from loguru import logger


class Node(BaseModel):
    kind: str
    name: str
    first_name: Optional[str] = None
    pyname: Optional[str] = None
    children: List['Node'] = []
    #children: List['Node'] = Field([], exclude=True, repr=False)
    exclude: Optional[bool] = False
    overload: Optional[bool] = False
    readonly: Optional[bool] = False

    cursor: Optional[cindex.Cursor] = Field(None, exclude=True, repr=False)
    visited: Optional[bool] = Field(False, exclude=True, repr=False)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            cindex.Cursor: lambda v: "Cursor Object"
        }

    def model_post_init(self, __context) -> None:
        self.first_name = self.name.split("::")[-1]
    '''
    def __init__(self, name: str, cursor: cindex.Cursor = None):
        self.name = name
        self.first_name = name.split("::")[-1]
        self.cursor = cursor
        self.children = []
        self.visited = False
    '''

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} kind={self.kind}, name={self.name}, pyname={self.pyname}>"

    def add_child(self, entry: "Node"):
        self.children.append(entry)

class Argument(BaseModel):
    default: Optional[Any] = None

class FunctionNode(Node):
    kind: str = 'function'
    arguments: Optional[Dict[str, Argument]] = {}
    return_type: Optional[str] = None
    omit_ret: Optional[bool] = False
    check_result: Optional[bool] = False

    def model_post_init(self, __context) -> None:
        super().model_post_init(__context)
        self.arguments = {k: Argument(**v) if isinstance(v, dict) else v for k, v in self.arguments.items()}


class CtorNode(Node):
    kind: str = 'ctor'


class FieldNode(Node):
    kind: str = 'field'


class MethodNode(Node):
    kind: str = 'method'


class StructBaseNode(Node):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    gen_wrapper: dict = None


class StructNode(StructBaseNode):
    kind: str = 'struct'


class ClassNode(StructBaseNode):
    kind: str = 'class'


class EnumNode(Node):
    kind: str = 'enum'


class TypedefNode(Node):
    kind: str = 'typedef'
    gen_init: bool = False
    gen_kw_init: bool = False
