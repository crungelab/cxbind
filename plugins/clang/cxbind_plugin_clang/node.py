from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Literal, Union, Any
from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
    ConfigDict,
    PrivateAttr,
    computed_field,
)

from clang import cindex
from loguru import logger

from cxbind.entry import Entry, EntryKey
from cxbind.spec import (
    Spec,
    ParamDirection,
    ParamSpec,
    Ownership,
    ReturnSpec,
    FunctionalSpec,
    StructuralSpec,
    FieldSpec,
)
from cxbind.facade import Facade
from cxbind.extra import StructuralExtra

if TYPE_CHECKING:
    from .pyname_registry import PyBinding


class Node(Entry):
    # Name for nodes the pyname registry doesn't track (no py_kind, or not yet
    # migrated). Loads from "pyname" so serialized nodes round-trip; dumping
    # goes through the computed `pyname` below instead.
    legacy_pyname: str | None = Field(
        None, validation_alias="pyname", exclude=True, repr=False
    )
    children: list["Node"] = Field(default_factory=list)
    parent: Optional["Node"] = Field(None, exclude=True, repr=False)

    spec: Spec | None = Field(None, exclude=True, repr=False)
    facade: Facade | None = Field(None, exclude=True, repr=False)

    # Private: not validated, not serialized, not part of the schema.
    # Shallow-copied by model_copy(), so clones share their source's binding.
    _binding: Optional[PyBinding] = PrivateAttr(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def binding(self) -> PyBinding | None:
        return self._binding

    @binding.setter
    def binding(self, value: PyBinding | None) -> None:
        self._binding = value

    @computed_field
    @property
    def pyname(self) -> str | None:
        if self._binding is not None:
            return self._binding.pyname
        return self.legacy_pyname

    @pyname.setter
    def pyname(self, value: str | None) -> None:
        if self._binding is not None:
            logger.warning(
                f"Setting pyname '{value}' on {self.name}, which has a binding "
                f"('{self._binding.pyname}'); the binding's name takes precedence"
            )
        self.legacy_pyname = value

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"kind={self.kind}, name={self.name}, signature={self.signature}, pyname={self.pyname}>"
        )

    def clone(self) -> "Node":
        # return self.model_copy(deep=True)
        return self.model_copy()

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

        if (
            cursor.kind
            in (
                cindex.CursorKind.TYPEDEF_DECL,
                cindex.CursorKind.TYPE_ALIAS_DECL,
            )
            and cursor.type.get_canonical().kind != cindex.TypeKind.FUNCTIONPROTO
        ):
            underlying = cursor.underlying_typedef_type
            cursor = underlying.get_declaration()
            logger.debug(f"Underlying typedef type spelling: {underlying.spelling}")

        if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            kind = "translation_unit"
        elif cursor.kind == cindex.CursorKind.NAMESPACE:
            kind = "namespace"
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
            if cursor.type.get_canonical().kind == cindex.TypeKind.FUNCTIONPROTO:
                kind = "function_prototype"
            else:
                # logger.debug(f"Unsupported cursor kind: {cursor.kind}")
                return None
        elif cursor.kind == cindex.CursorKind.CLASS_TEMPLATE:
            kind = "class_template"
        elif cursor.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
            kind = "function_template"
        elif cursor.kind == cindex.CursorKind.TYPE_ALIAS_DECL:
            kind = "type_alias"
        else:
            # logger.debug(f"Unsupported cursor kind: {cursor.kind}")
            return None
            # raise ValueError(f"Unsupported cursor kind: {cursor.kind}")

        name = cls.spell(cursor)

        if overload:
            key = EntryKey.build(
                kind=kind,
                name=name,
                signature=cursor.type.spelling,
            )
        else:
            key = EntryKey.build(kind=kind, name=name)

        logger.debug(f"Entry key: {key}")
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

    def clone(self) -> "DeclNode":
        other: "DeclNode" = super().clone()
        other.cursor = self.cursor
        return other


class NamespaceNode(DeclNode):
    kind: Literal["namespace"] = "namespace"


class TemplateNode(Node):
    pass


class RootNode(Node):
    kind: Literal["root"] = "root"


class Parameter(BaseModel):
    name: str
    type: Type
    default: object | None = None
    direction: ParamDirection = ParamDirection.IN

    cursor: cindex.Cursor | None = Field(None, exclude=True, repr=False)
    spec: ParamSpec | None = Field(None, exclude=True, repr=False)
    facade: Facade | None = Field(None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def is_out(self) -> bool:
        return self.direction in (ParamDirection.OUT, ParamDirection.INOUT)


class CallbackParam(Parameter):
    function_prototype: FunctionPrototypeNode | None = None


class ReturnValue(BaseModel):
    type: Type
    spec: ReturnSpec | None = Field(None, exclude=True, repr=False)
    ownership: Ownership = Ownership.AUTOMATIC

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FunctionalNode(DeclNode):
    spec: FunctionalSpec | None = Field(None, exclude=True, repr=False)
    params: list[Parameter] = Field(default_factory=list)
    returns: ReturnValue | None = None
    mogrified: bool = False


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
    spec: FieldSpec | None = Field(None, exclude=True, repr=False)
    type: Type | None = Field(None, exclude=True, repr=False)


class StructuralNode(DeclNode):
    spec: StructuralSpec | None = Field(None, exclude=True, repr=False)

    # This node's extras: a private copy of spec.extra that transforms may
    # add to. The spec itself is never modified (specs are shared between units).
    _extra: StructuralExtra | None = PrivateAttr(default=None)

    @property
    def extra(self) -> StructuralExtra:
        if self._extra is None:
            self._extra = (
                self.spec.extra.model_copy(deep=True)
                if self.spec is not None
                else StructuralExtra()
            )
        return self._extra


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
    # Set by EnumExportResolver during synthesis; None = not yet decided.
    exported: bool | None = Field(None, exclude=True, repr=False)


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
