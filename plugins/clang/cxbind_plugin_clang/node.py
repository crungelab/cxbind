from typing_extensions import Annotated
from typing import Optional, Literal, Union

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict

from clang import cindex
from loguru import logger

from cxbind.spec import Spec, ArgSpec, ArgDirection, ReturnSpec
from cxbind.facade import Facade


class Node(BaseModel):
    kind: str
    name: str
    signature: str | None = None
    pyname: str | None = None
    #children: list["Node"] = []
    children: list["Node"] = Field(default_factory=list)
    parent: Optional["Node"] = None

    #cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)
    spec: Spec | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def key(self) -> str:
        if self.signature:
            return f"{self.kind}@{self.name}@{self.signature}"
        return f"{self.kind}@{self.name}"

    @property
    def first_name(self) -> str:
        return self.name.split("::")[-1]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} kind={self.kind}, name={self.name}, pyname={self.pyname}>"

    @classmethod
    def spell(cls, cursor: cindex.Cursor) -> str:
        if cursor is None:
            return ""
        elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ""
        else:
            res = cls.spell(cursor.semantic_parent)
            if res != "":
                return res + "::" + cursor.spelling
        return cursor.spelling

    """
    @classmethod
    def make_key(cls, cursor: cindex.Cursor, overload: bool = False) -> str:
        name = cls.spell(cursor)

        if overload:
            key = f"{name}@{cursor.type.spelling}"
        else:
            key = name

        return key

    @classmethod
    def make_kind(cls, cursor: cindex.Cursor) -> str:
        kind = None
        if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            kind = "translation_unit"
        elif cursor.kind == cindex.CursorKind.CLASS_DECL:
            kind = "class"
        elif cursor.kind == cindex.CursorKind.STRUCT_DECL:
            kind = "struct"
        elif cursor.kind == cindex.CursorKind.ENUM_DECL:
            kind = "enum"
        elif cursor.kind == cindex.CursorKind.FIELD_DECL:
            kind = "field"
        elif cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            kind = "function"
        elif cursor.kind == cindex.CursorKind.CXX_METHOD:
            kind = "method"
        elif cursor.kind == cindex.CursorKind.CONSTRUCTOR:
            kind = "ctor"
        elif cursor.kind == cindex.CursorKind.TYPEDEF_DECL:
            kind = "typedef"
        elif cursor.kind == cindex.CursorKind.CLASS_TEMPLATE:
            kind = "class_template"
        elif cursor.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
            kind = "function_template"

        return kind

    """
    @classmethod
    def make_key(cls, cursor: cindex.Cursor, overload: bool = False) -> str:
        kind = None
        if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            kind = "translation_unit"
        elif cursor.kind == cindex.CursorKind.CLASS_DECL:
            kind = "class"
        elif cursor.kind == cindex.CursorKind.STRUCT_DECL:
            kind = "struct"
        elif cursor.kind == cindex.CursorKind.ENUM_DECL:
            kind = "enum"
        elif cursor.kind == cindex.CursorKind.FIELD_DECL:
            kind = "field"
        elif cursor.kind == cindex.CursorKind.FUNCTION_DECL:
            kind = "function"
        elif cursor.kind == cindex.CursorKind.CXX_METHOD:
            kind = "method"
        elif cursor.kind == cindex.CursorKind.CONSTRUCTOR:
            kind = "ctor"
        elif cursor.kind == cindex.CursorKind.TYPEDEF_DECL:
            kind = "typedef"
        elif cursor.kind == cindex.CursorKind.CLASS_TEMPLATE:
            kind = "class_template"
        elif cursor.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
            kind = "function_template"

        name = cls.spell(cursor)

        if overload:
            key = f"{kind}@{name}@{cursor.type.spelling}"
        else:
            key = f"{kind}@{name}"

        return key

    def add_child(self, child: "Node"):
        child.parent = self
        self.children.append(child)

    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()


class Type(BaseModel):
    spelling: str
    base_name: str
    type: cindex.Type | None = Field(None, exclude=True, repr=False)
    base_spec: Spec | None = Field(None, exclude=True, repr=False)
    facade: Facade | None = Field(None, exclude=True, repr=False)
    model_config = ConfigDict(arbitrary_types_allowed=True)


class DeclNode(Node):
    #pass
    cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)


class TemplateNode(Node):
    pass


class RootNode(Node):
    kind: Literal["root"] = "root"


class Argument(BaseModel):
    name: str
    type: Type
    #type: str
    default: object | None = None
    direction: ArgDirection = ArgDirection.IN

    cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)
    spec: ArgSpec | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def is_out(self) -> bool:
        return self.direction in (ArgDirection.OUT, ArgDirection.INOUT)


class ReturnValue(BaseModel):
    type: Type
    #type: str
    #cursor: cindex.Type | None = Field(None, exclude=True, repr=False)
    spec: ReturnSpec | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FunctionalNode(DeclNode):
    #args: list[Argument] | None = []
    args: list[Argument] = Field(default_factory=list)
    returns: ReturnValue | None = None


class FunctionNode(FunctionalNode):
    kind: Literal["function"]


class FunctionTemplateSpecializationNode(FunctionNode):
    kind: Literal["function_template_specialization"]


class FunctionTemplateNode(TemplateNode):
    kind: Literal["function_template"]


class MethodNode(FunctionalNode):
    kind: Literal["method"]


class CtorNode(FunctionalNode):
    kind: Literal["ctor"]


#class FieldNode(Node):
class FieldNode(DeclNode):
    kind: Literal["field"]


class StructuralNode(DeclNode):
    constructible: bool = True
    has_constructor: bool = False


class StructNode(StructuralNode):
    kind: Literal["struct"]


class ClassNode(StructuralNode):
    kind: Literal["class"]


class ClassTemplateSpecializationNode(ClassNode):
    kind: Literal["class_template_specialization"]


class ClassTemplateNode(TemplateNode):
    kind: Literal["class_template"]


class EnumNode(DeclNode):
    kind: Literal["enum"]


NodeUnion = Union[
    StructNode,
    ClassNode,
    ClassTemplateNode,
    FieldNode,
    FunctionNode,
    FunctionTemplateNode,
    MethodNode,
    CtorNode,
    EnumNode,
]


def validate_node_dict(v: dict[str, Node]) -> dict[str, Node]:
    # logger.debug(f"validate_node_dict: {v}")
    data = {}
    for key, value in v.items():
        if "@" in key:
            kind, name, signature = None, None, None
            parts = key.split("@")

            if len(parts) == 2:
                kind, name = parts
            elif len(parts) == 3:
                kind, name, signature = parts

            value["kind"] = kind
            value["name"] = name
            value["signature"] = signature

            data[key] = value
        else:
            data[key] = value
    return data


NodeDict = Annotated[dict[str, NodeUnion], BeforeValidator(validate_node_dict)]
