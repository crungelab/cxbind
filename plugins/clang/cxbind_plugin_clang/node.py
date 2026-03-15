from __future__ import annotations

from typing import Optional, Literal, Union, Any
from typing_extensions import Annotated

from pydantic import BaseModel, Field, TypeAdapter, ConfigDict

from clang import cindex
from loguru import logger

from cxbind.entry import Entry, EntryKey
from cxbind.spec import Spec, ArgSpec, ArgDirection, ReturnSpec, FunctionalSpec
from cxbind.facade import Facade


class Node(Entry):
    # kind: str
    # name: str
    # signature: str | None = None

    pyname: str | None = None
    children: list["Node"] = Field(default_factory=list)
    # parent: Optional["Node"] = None
    parent: Optional["Node"] = Field(None, exclude=True, repr=False)

    spec: Spec | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    """
    @property
    def key(self) -> EntryKey:
        return EntryKey.build(
            kind=self.kind,
            name=self.name,
            signature=self.signature,
        )

    @property
    def key_string(self) -> str:
        return self.key.dump()
    
    @property
    def first_name(self) -> str:
        return self.name.split("::")[-1]
    """

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"kind={self.kind}, name={self.name}, signature={self.signature}, pyname={self.pyname}>"
        )

    @classmethod
    def spell(cls, cursor: cindex.Cursor) -> str:
        if cursor is None:
            return ""
        if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ""

        res = cls.spell(cursor.semantic_parent)
        if res:
            return res + "::" + cursor.spelling
        return cursor.spelling

    @classmethod
    def make_key(
        cls,
        cursor: cindex.Cursor,
        overload: bool = False,
    ) -> EntryKey | None:
        kind = None

        if cursor.kind in (
            cindex.CursorKind.TYPEDEF_DECL,
            cindex.CursorKind.TYPE_ALIAS_DECL,
        ):
            underlying = cursor.underlying_typedef_type
            cursor = underlying.get_declaration()
            # logger.debug(f"Underlying typedef type spelling: {underlying.spelling}")

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
        elif cursor.kind == cindex.CursorKind.TYPE_ALIAS_DECL:
            kind = "type_alias"
        else:
            return None

        name = cls.spell(cursor)

        if overload:
            key = EntryKey.build(
                kind=kind,
                name=name,
                signature=cursor.type.spelling,
            )
        else:
            key = EntryKey.build(kind=kind, name=name)

        logger.debug(f"Spec key: {key}")
        return key

    def add_child(self, child: "Node") -> None:
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
    cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TemplateNode(Node):
    pass


class RootNode(Node):
    kind: Literal["root"] = "root"


class Argument(BaseModel):
    name: str
    type: Type
    default: object | None = None
    direction: ArgDirection = ArgDirection.IN

    cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)
    spec: ArgSpec | None = Field(None, exclude=True, repr=False)
    function_prototype: FunctionPrototypeNode | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def is_out(self) -> bool:
        return self.direction in (ArgDirection.OUT, ArgDirection.INOUT)


class ReturnValue(BaseModel):
    type: Type
    spec: ReturnSpec | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FunctionalNode(DeclNode):
    spec: FunctionalSpec | None = Field(None, exclude=True, repr=False)
    args: list[Argument] = Field(default_factory=list)
    returns: ReturnValue | None = None


class FunctionPrototypeNode(FunctionalNode):
    kind: Literal["function_prototype"]


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


NodeUnion = Annotated[
    Union[
        RootNode,
        StructNode,
        ClassNode,
        ClassTemplateNode,
        FieldNode,
        FunctionNode,
        FunctionTemplateNode,
        MethodNode,
        CtorNode,
        EnumNode,
    ],
    Field(discriminator="kind"),
]

NODE_ADAPTER = TypeAdapter(NodeUnion)
