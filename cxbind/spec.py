from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union

from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic_core import core_schema
from loguru import logger

from .entry import Entry, EntryKey, EntryKeySet

# from .extra import special_methods, Extra, ExtraProperty, ExtraMethodUnion
from .extra import StructuralExtra
from .facade import WRAPPER_FACADES, FacadeUnion


class Spec(Entry):
    alias: str | None = None
    pyname: str | None = None
    exclude: bool = False
    overload: bool = False
    readonly: bool = False
    facade: FacadeUnion | None = None

    model_config = ConfigDict(extra="forbid")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"kind={self.kind}, name={self.name}, signature={self.signature}, pyname={self.pyname}>"
        )


class NamespaceSpec(Spec):
    kind: Literal["namespace"]


class TemplateSpec(Spec):
    """Base for template specs.

    Normalizes the `specializations` list so each item is a dict carrying the
    template's name. Accepted item forms:
      - dict:        used as-is, inheriting the parent's name if absent
      - list/tuple:  treated as template args
      - scalar:      treated as a name
    Each specialization's `kind` comes from the default on its model.
    """

    @model_validator(mode="before")
    @classmethod
    def _normalize_specializations(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        specs = data.get("specializations")
        if not specs:
            return data

        parent_name = data.get("name")
        normalized = []
        for item in specs:
            if isinstance(item, dict):
                if "name" not in item and parent_name is not None:
                    item = {"name": parent_name, **item}
                normalized.append(item)
            elif isinstance(item, (list, tuple)):
                normalized.append({"name": parent_name, "template_args": list(item)})
            else:
                normalized.append({"name": str(item)})

        return {**data, "specializations": normalized}


class ParamDirection(str, Enum):
    IN = "in"
    OUT = "out"
    INOUT = "inout"


class ParamSpec(BaseModel):
    optional: bool = False
    default: Any | None = None
    facade: FacadeUnion | None = None
    direction: ParamDirection = ParamDirection.IN

    @property
    def is_out(self) -> bool:
        return self.direction in (ParamDirection.OUT, ParamDirection.INOUT)


class Ownership(str, Enum):
    AUTOMATIC = "automatic"  # auto-detect based on type, default behavior
    # -> automatic (sk_sp for ref-counted, reference_internal for raw ptr, etc.)
    OWNED = "owned"  # dynamically allocated, Python takes ownership
    # → take_ownership (raw ptr) or automatic (sk_sp holder)
    BORROWED = "borrowed"  # parent object owns it, keep parent alive
    # → reference_internal (ptr/lref)
    SHARED = "shared"  # sk_sp ref-counted, holder manages it
    # → no RVP needed, holder does the work
    REF = "ref"  # C++ manages lifetime globally, just reference it
    # → reference (dangerous, use sparingly)
    VALUE = "value"  # copy semantics
    # → copy
    MOVE = "move"  # rvalue, move into Python-owned instance
    # → move


class ReturnSpec(BaseModel):
    facade: FacadeUnion | None = None
    ownership: Ownership = Ownership.AUTOMATIC


class FunctionalSpec(Spec):
    params: dict[str, ParamSpec] = Field(default_factory=dict)
    returns: ReturnSpec | None = None
    omit_ret: bool = False

    @field_validator("params", mode="before")
    @classmethod
    def _parse_parameters(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        return {
            k: val if isinstance(val, (dict, ParamSpec)) else {"default": val}
            for k, val in v.items()
        }


class FunctionPrototypeSpec(FunctionalSpec):
    kind: Literal["function_prototype"]


class FunctionSpec(FunctionalSpec):
    kind: Literal["function"]


class FunctionTemplateSpecializationSpec(FunctionSpec):
    # Defaulted: specializations are nested under their template, so the
    # kind is implied and never supplied by the input.
    kind: Literal["function_template_specialization"] = (
        "function_template_specialization"
    )
    template_args: list[str] = Field(default_factory=list)


class FunctionTemplateSpec(TemplateSpec):
    kind: Literal["function_template"]
    specializations: list[FunctionTemplateSpecializationSpec] = Field(
        default_factory=list
    )


class MethodSpec(FunctionalSpec):
    kind: Literal["method"]


class CtorSpec(FunctionalSpec):
    kind: Literal["ctor"]


class FieldSpec(Spec):
    kind: Literal["field"]
    flatten: bool = False

class StubSpec(BaseModel):
    # Dotted names to import: "collections.abc.Iterator" -> from collections.abc import Iterator
    imports: list[str] = []
    # Stub lines appended to the class body, for members bound by hand.
    members: list[str] = []

    @field_validator("members", mode="before")
    @classmethod
    def split_block(cls, v):
        # Accept a YAML block string as well as a list of lines.
        return v.splitlines() if isinstance(v, str) else v

class StructuralSpec(Spec):
    extends: list[str] | None = None
    identity: str | None = None
    wrapper: str | None = None
    holder: str | None = None
    ownership: Ownership = Ownership.AUTOMATIC
    extra: StructuralExtra = Field(default_factory=StructuralExtra)
    stub: StubSpec = Field(default_factory=StubSpec)

    @model_validator(mode="before")
    @classmethod
    def _apply_wrapper(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        wrapper = data.get("wrapper")
        if wrapper is None or data.get("facade") is not None:
            return data

        if wrapper in WRAPPER_FACADES:
            facade = {"kind": wrapper}
        else:
            facade = {"kind": "wrapper", "wrapper": wrapper}

        return {**data, "facade": facade}


class StructSpec(StructuralSpec):
    kind: Literal["struct"]


class ClassSpec(StructuralSpec):
    kind: Literal["class"]


class ClassTemplateSpecializationSpec(ClassSpec):
    # Defaulted: see FunctionTemplateSpecializationSpec.
    kind: Literal["class_template_specialization"] = "class_template_specialization"
    template_args: list[str] = Field(default_factory=list)


class ClassTemplateSpec(TemplateSpec):
    kind: Literal["class_template"]
    specializations: list[ClassTemplateSpecializationSpec] = Field(default_factory=list)


class EnumSpec(Spec):
    kind: Literal["enum"]


SpecUnion = Annotated[
    Union[
        StructSpec,
        ClassSpec,
        ClassTemplateSpec,
        FieldSpec,
        FunctionPrototypeSpec,
        FunctionSpec,
        FunctionTemplateSpec,
        MethodSpec,
        CtorSpec,
        EnumSpec,
    ],
    Field(discriminator="kind"),
]

SPEC_ADAPTER = TypeAdapter(SpecUnion)


class SpecMap(dict[EntryKey, SpecUnion]):
    @classmethod
    def _normalize_input(cls, value: Any) -> dict[EntryKey, Any]:
        if value is None:
            return {}

        if isinstance(value, cls):
            return dict(value)

        if not isinstance(value, dict):
            raise TypeError(f"SpecMap input must be a dict, got {type(value).__name__}")

        out: dict[EntryKey, Any] = {}

        for raw_key, raw_value in value.items():
            key = raw_key if isinstance(raw_key, EntryKey) else EntryKey.parse(raw_key)

            if not isinstance(raw_value, dict):
                raise TypeError(f"Spec entry for {key} must be a dict")

            item = raw_value.copy()
            item["kind"] = key.kind
            item["name"] = key.name
            if key.signature is not None:
                item["signature"] = key.signature

            out[key] = item

        return out

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        dict_schema = handler.generate_schema(dict[EntryKey, SpecUnion])

        return core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls._normalize_input),
                dict_schema,
                core_schema.no_info_plain_validator_function(cls),
            ]
        )


def create_spec(key: EntryKey | str, **kwargs: Any) -> SpecUnion:
    spec_key = EntryKey.parse(key) if isinstance(key, str) else key

    spec_cls = {
        "namespace": NamespaceSpec,
        "function": FunctionSpec,
        "function_prototype": FunctionPrototypeSpec,
        "function_template": FunctionTemplateSpec,
        "method": MethodSpec,
        "ctor": CtorSpec,
        "field": FieldSpec,
        "struct": StructSpec,
        "class": ClassSpec,
        "class_template": ClassTemplateSpec,
        "enum": EnumSpec,
    }.get(spec_key.kind)

    if spec_cls is None:
        logger.error(f"Unknown spec kind: {spec_key.kind}")
        raise ValueError(f"Unknown spec kind: {spec_key.kind}")

    return spec_cls(
        kind=spec_key.kind,
        name=spec_key.name,
        signature=spec_key.signature,
        **kwargs,
    )
