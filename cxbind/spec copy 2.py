from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union

from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)
from loguru import logger

from .extra import special_methods, Extra, ExtraProperty, ExtraMethodUnion
from .facade import WRAPPER_FACADES, FacadeUnion


class SpecKey(BaseModel):
    kind: str
    name: str
    signature: str | None = None

    model_config = ConfigDict(frozen=True)

    @property
    def value(self) -> str:
        if self.signature:
            return f"{self.kind}@{self.name}@{self.signature}"
        return f"{self.kind}@{self.name}"

    @classmethod
    def parse(cls, value: str) -> "SpecKey":
        parts = value.split("@")

        if len(parts) == 2:
            kind, name = parts
            signature = None
        elif len(parts) == 3:
            kind, name, signature = parts
        else:
            raise ValueError(f"Invalid spec key: {value}")

        return cls(kind=kind, name=name, signature=signature)

    @classmethod
    def build(
        cls,
        *,
        kind: str,
        name: str,
        signature: str | None = None,
    ) -> "SpecKey":
        return cls(kind=kind, name=name, signature=signature)

    """
    def __str__(self) -> str:
        return self.value
    """

class Spec(BaseModel):
    kind: str
    name: str
    alias: str | None = None
    signature: str | None = None
    pyname: str | None = None
    exclude: bool = False
    overload: bool = False
    readonly: bool = False
    facade: FacadeUnion | None = None

    model_config = ConfigDict(extra="forbid")

    @property
    def key(self) -> SpecKey:
        return SpecKey.build(
            kind=self.kind,
            name=self.name,
            signature=self.signature,
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"kind={self.kind}, name={self.name}, signature={self.signature}, pyname={self.pyname}>"
        )


class TemplateSpec(Spec):
    pass


class ArgDirection(str, Enum):
    IN = "in"
    OUT = "out"
    INOUT = "inout"


class ArgSpec(BaseModel):
    optional: bool = False
    default: Any | None = None
    facade: FacadeUnion | None = None
    direction: ArgDirection = ArgDirection.IN

    @property
    def is_out(self) -> bool:
        return self.direction in (ArgDirection.OUT, ArgDirection.INOUT)


class ReturnSpec(BaseModel):
    pass


class FunctionalSpec(Spec):
    args: dict[str, ArgSpec] = Field(default_factory=dict)
    returns: ReturnSpec | None = None
    omit_ret: bool = False

    @field_validator("args", mode="before")
    @classmethod
    def _parse_arguments(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        return {
            k: val if isinstance(val, (dict, ArgSpec)) else {"default": val}
            for k, val in v.items()
        }


class FunctionSpec(FunctionalSpec):
    kind: Literal["function"]


class FunctionTemplateSpecializationSpec(FunctionSpec):
    kind: Literal["function_template_specialization"] = (
        "function_template_specialization"
    )
    args: list[str]


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
                normalized.append({"name": data.get("name"), "args": list(item)})
            else:
                normalized.append({"name": str(item)})

        data["specializations"] = normalized
        return data


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
    args: list[str]


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
                normalized.append({"name": data.get("name"), "args": list(item)})
            else:
                normalized.append({"name": str(item)})

        data["specializations"] = normalized
        return data


class EnumSpec(Spec):
    kind: Literal["enum"]


class TypeAliasSpec(Spec):
    kind: Literal["type_alias"]
    wrapper: str | None = None

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

class TypeDefSpec(Spec):
    kind: Literal["typedef"]
    wrapper: str | None = None

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
        TypeAliasSpec,
        TypeDefSpec,
    ],
    Field(discriminator="kind"),
]

SPEC_ADAPTER = TypeAdapter(SpecUnion)

def validate_spec_dict(v: Any) -> Any:
    """
    Pre-process dictionary keys of the form:

        kind@name
        kind@name@signature

    into SpecKey keys and explicit data fields before Pydantic validates.
    """
    if not isinstance(v, dict):
        return v

    data = {}
    for key, value in v.items():
        spec_key = key if isinstance(key, SpecKey) else SpecKey.parse(key)

        if isinstance(value, dict):
            val_copy = value.copy()
            val_copy["kind"] = spec_key.kind
            val_copy["name"] = spec_key.name
            if spec_key.signature is not None:
                val_copy["signature"] = spec_key.signature
            data[spec_key] = val_copy
        else:
            data[spec_key] = value

    return data
'''
def validate_spec_dict(v: Any) -> Any:
    """
    Pre-process dictionary keys of the form:

        kind@name
        kind@name@signature

    into explicit data fields before Pydantic validates.
    """
    if not isinstance(v, dict):
        return v

    data = {}
    for key, value in v.items():
        if "@" in key and isinstance(value, dict):
            val_copy = value.copy()
            spec_key = SpecKey.parse(key)

            val_copy["kind"] = spec_key.kind
            val_copy["name"] = spec_key.name
            if spec_key.signature is not None:
                val_copy["signature"] = spec_key.signature

            data[key] = val_copy
        else:
            data[key] = value

    return data
'''

#SpecDict = Annotated[dict[str, SpecUnion], BeforeValidator(validate_spec_dict)]
SpecDict = Annotated[dict[SpecKey, SpecUnion], BeforeValidator(validate_spec_dict)]


def create_spec(key: SpecKey | str, **kwargs: Any) -> SpecUnion:
    spec_key = SpecKey.parse(key) if isinstance(key, str) else key

    spec_cls = {
        "function": FunctionSpec,
        "function_template": FunctionTemplateSpec,
        "method": MethodSpec,
        "ctor": CtorSpec,
        "field": FieldSpec,
        "struct": StructSpec,
        "class": ClassSpec,
        "class_template": ClassTemplateSpec,
        "enum": EnumSpec,
        "type_alias": TypeAliasSpec,
    }.get(spec_key.kind)

    if spec_cls is None:
        raise ValueError(f"Unknown spec kind: {spec_key.kind}")

    return spec_cls(
        kind=spec_key.kind,
        name=spec_key.name,
        signature=spec_key.signature,
        **kwargs,
    )
