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
    BeforeValidator,
)
from pydantic_core import core_schema
from loguru import logger

from .entry import Entry, EntryKey, EntryKeySet
from .extra import special_methods, Extra, ExtraProperty, ExtraMethodUnion
from .facade import WRAPPER_FACADES, FacadeUnion

"""
class EntryKey(BaseModel):
    kind: str
    name: str
    signature: str | None = None

    model_config = ConfigDict(frozen=True)

    def dump(self) -> str:
        if self.signature is None:
            return f"{self.kind}@{self.name}"
        return f"{self.kind}@{self.name}@{self.signature}"

    def __str__(self) -> str:
        return self.dump()

    @classmethod
    def parse(cls, value: str) -> "EntryKey":
        parts = value.split("@", 2)

        if len(parts) == 2:
            kind, name = parts
            signature = None
        elif len(parts) == 3:
            kind, name, signature = parts
        else:
            raise ValueError(f"Invalid spec key: {value!r}")

        return cls(kind=kind, name=name, signature=signature)

    @classmethod
    def build(
        cls,
        *,
        kind: str,
        name: str,
        signature: str | None = None,
    ) -> "EntryKey":
        return cls(kind=kind, name=name, signature=signature)

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        model_schema = handler(source)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.parse),
                    ]
                ),
                model_schema,
            ]
        )

def normalize_entry_key_set(value: Any) -> Any:
    if value is None:
        return set()

    if not isinstance(value, (list, tuple, set, frozenset)):
        return value

    out: set[EntryKey] = set()
    for item in value:
        if isinstance(item, EntryKey):
            out.add(item)
        elif isinstance(item, str):
            out.add(EntryKey.parse(item))
        else:
            raise TypeError(f"Invalid EntryKey entry: {item!r}")
    return out


EntryKeySet = Annotated[set[EntryKey], BeforeValidator(normalize_entry_key_set)]
"""


class Spec(Entry):
    # kind: str
    # name: str
    # signature: str | None = None

    alias: str | None = None
    pyname: str | None = None
    exclude: bool = False
    overload: bool = False
    readonly: bool = False
    facade: FacadeUnion | None = None

    model_config = ConfigDict(extra="forbid")

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
    """

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"kind={self.kind}, name={self.name}, signature={self.signature}, pyname={self.pyname}>"
        )


class TemplateSpec(Spec):
    pass


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


class ReturnSpec(BaseModel):
    facade: FacadeUnion | None = None


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


class FunctionSpec(FunctionalSpec):
    kind: Literal["function"]


class FunctionTemplateSpecializationSpec(FunctionSpec):
    kind: Literal["function_template_specialization"] = (
        "function_template_specialization"
    )
    #args: list[str]
    template_args: list[str] = Field(default_factory=list)


class FunctionTemplateSpec(TemplateSpec):
    kind: Literal["function_template"]
    specializations: list[FunctionTemplateSpecializationSpec] = Field(
        default_factory=list
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_specializations(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        specs = data.get("specializations")
        if not specs:
            return data

        normalized = []
        for item in specs:
            if isinstance(item, dict):
                if "name" not in item and "name" in data:
                    item = {"name": data["name"], **item}
                normalized.append(item)
            elif isinstance(item, (list, tuple)):
                normalized.append({"name": data.get("name"), "template_args": list(item)})
            else:
                normalized.append({"name": str(item)})

        data["specializations"] = normalized
        return data


class FunctionPrototypeSpec(FunctionalSpec):
    kind: Literal["function_prototype"]


class MethodSpec(FunctionalSpec):
    kind: Literal["method"]


class CtorSpec(FunctionalSpec):
    kind: Literal["ctor"]


class FieldSpec(Spec):
    kind: Literal["field"]


class StructuralExtra(Extra):
    properties: list[ExtraProperty] = Field(default_factory=list)
    methods: list[ExtraMethodUnion] = Field(default_factory=list)

    def add_property(self, property_: ExtraProperty) -> None:
        self.properties.append(property_)

    def add_method(self, method: ExtraMethodUnion) -> None:
        self.methods.append(method)

    @field_validator("properties", mode="before")
    @classmethod
    def _normalize_properties(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        normalized = []
        for key, item in v.items():
            if isinstance(item, dict):
                if "name" not in item:
                    item = {"name": key, **item}
                normalized.append(item)

        return normalized

    @field_validator("methods", mode="before")
    @classmethod
    def _normalize_methods(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        normalized = []
        for key, item in v.items():
            if isinstance(item, dict):
                if "name" not in item:
                    item = {"name": key, **item}
                if item["name"] in special_methods and "kind" not in item:
                    item["kind"] = item["name"]
                else:
                    item["kind"] = "standard"
                normalized.append(item)

        return normalized


class StructuralSpec(Spec):
    extends: list[str] | None = None
    wrapper: str | None = None
    holder: str | None = None
    extra: StructuralExtra = Field(default_factory=StructuralExtra)

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if "wrapper" in data:
            if data["wrapper"] in WRAPPER_FACADES:
                data["facade"] = {"kind": data["wrapper"]}
            else:
                data["facade"] = {"kind": "wrapper", "wrapper": data["wrapper"]}

        return data


class StructSpec(StructuralSpec):
    kind: Literal["struct"]


class ClassSpec(StructuralSpec):
    kind: Literal["class"]


class ClassTemplateSpecializationSpec(ClassSpec):
    kind: Literal["class_template_specialization"] = "class_template_specialization"
    #args: list[str]
    template_args: list[str] = Field(default_factory=list)


class ClassTemplateSpec(TemplateSpec):
    kind: Literal["class_template"]
    specializations: list[ClassTemplateSpecializationSpec] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalize_specializations(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        specs = data.get("specializations")
        if not specs:
            return data

        normalized = []
        for item in specs:
            if isinstance(item, dict):
                if "name" not in item and "name" in data:
                    item = {"name": data["name"], **item}
                normalized.append(item)
            elif isinstance(item, (list, tuple)):
                normalized.append({"name": data.get("name"), "template_args": list(item)})
            else:
                normalized.append({"name": str(item)})

        data["specializations"] = normalized
        return data


class EnumSpec(Spec):
    kind: Literal["enum"]


SpecUnion = Annotated[
    Union[
        StructSpec,
        ClassSpec,
        ClassTemplateSpec,
        FieldSpec,
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
