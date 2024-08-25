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

    def model_post_init(self, __context: Any) -> None:
        self.first_name = self.name.split("::")[-1]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} kind={self.kind}, name={self.name}, pyname={self.pyname}>"

    def add_child(self, child: "Node"):
        self.children.append(child)

class Argument(BaseModel):
    default: Optional[Any] = None

class FunctionBaseNode(Node):
    arguments: Optional[Dict[str, Argument]] = {}
    return_type: Optional[str] = None
    omit_ret: Optional[bool] = False
    check_result: Optional[bool] = False

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self.arguments = {k: Argument(**v) if isinstance(v, dict) else v for k, v in self.arguments.items()}

class FunctionNode(FunctionBaseNode):
    kind: str = 'function'

class MethodNode(FunctionBaseNode):
    kind: str = 'method'

class CtorNode(FunctionBaseNode):
    kind: str = 'ctor'

class FieldNode(Node):
    kind: str = 'field'


class StructBaseNode(Node):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    gen_wrapper: dict = None
    holder: Optional[str] = None


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
