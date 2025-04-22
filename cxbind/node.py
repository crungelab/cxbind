from typing_extensions import Annotated
from typing import List, Dict, Optional, Any, Literal, Union

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict

from clang import cindex
from loguru import logger


class Node(BaseModel):
    kind: str
    name: str
    first_name: Optional[str] = None
    pyname: Optional[str] = None
    children: List["Node"] = []
    exclude: Optional[bool] = False
    overload: Optional[bool] = False
    readonly: Optional[bool] = False

    cursor: Optional[cindex.Cursor] = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
        self.arguments = {
            k: Argument(**v) if isinstance(v, dict) else v
            for k, v in self.arguments.items()
        }


class FunctionNode(FunctionBaseNode):
    kind: Literal["function"]


class MethodNode(FunctionBaseNode):
    kind: Literal["method"]


class CtorNode(FunctionBaseNode):
    kind: Literal["ctor"]


class FieldNode(Node):
    kind: Literal["field"]


class StructBaseNode(Node):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    wrapper: str = None
    holder: Optional[str] = None


class StructNode(StructBaseNode):
    kind: Literal["struct"]


class ClassNode(StructBaseNode):
    kind: Literal["class"]

class ClassSpecializationNode(ClassNode):
    kind: Literal["class_specialization"]
    args: List[str] = []

class ClassTemplateSpecialization(BaseModel):
    name: str
    args: List[str]
    
class ClassTemplateNode(StructBaseNode):
    kind: Literal["class_template"]
    specializations: List[ClassTemplateSpecialization] = []


class EnumNode(Node):
    kind: Literal["enum"]


class TypedefNode(Node):
    kind: Literal["typedef"]
    gen_init: bool = False
    gen_kw_init: bool = False


NodeUnion = Union[
    StructNode,
    ClassNode,
    ClassTemplateNode,
    FieldNode,
    FunctionNode,
    MethodNode,
    CtorNode,
    EnumNode,
    TypedefNode,
]


def validate_node_dict(v: dict[str, Node]) -> dict[str, Node]:
    # logger.debug(f"validate_node_dict: {v}")
    data = {}
    for key, value in v.items():
        if "." in key:
            kind, name = key.split(".")
            value["name"] = name
            value["kind"] = kind
            data[name] = value
        else:
            data[key] = value
    return data


NodeDict = Annotated[dict[str, NodeUnion], BeforeValidator(validate_node_dict)]
