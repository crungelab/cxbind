from typing import Any, Literal, Union
from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
    ConfigDict,
    field_validator,
    model_validator,
)
from loguru import logger

from .extra import special_methods, Extra, ExtraMethod, ExtraProperty, ExtraMethodUnion
from .facade import ArgFacadeUnion

class Spec(BaseModel):
    kind: str
    name: str
    alias: str | None = None
    signature: str | None = None
    pyname: str | None = None
    exclude: bool = False
    overload: bool = False
    readonly: bool = False

    # model_config = ConfigDict(arbitrary_types_allowed=True)
    model_config = ConfigDict(extra="forbid")

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


class TemplateSpec(Spec):
    pass


class ArgSpec(BaseModel):
    optional: bool = False
    default: Any | None = None
    facade: ArgFacadeUnion | None = None


class FunctionalSpec(Spec):
    args: dict[str, ArgSpec] = Field(default_factory=dict)
    return_type: str | None = None
    omit_ret: bool = False
    check_result: bool = False

    @field_validator("args", mode="before")
    @classmethod
    def _parse_arguments(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        # Coerce raw values into a format Pydantic can parse into an Argument model
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


class MethodSpec(FunctionalSpec):
    kind: Literal["method"]


class CtorSpec(FunctionalSpec):
    kind: Literal["ctor"]


class FieldSpec(Spec):
    kind: Literal["field"]


class StructuralExtra(Extra):
    properties: list[ExtraProperty] = Field(default_factory=list)
    methods: list[ExtraMethodUnion] = Field(default_factory=list)

    def add_property(self, propery: ExtraProperty) -> None:
        self.properties.append(property)

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
        logger.debug(f"Normalizing methods: {v}")
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

        logger.debug(f"Normalized methods: {normalized}")
        return normalized


class StructuralSpec(Spec):
    extends: list[str] | None = None
    wrapper: str | None = None
    holder: str | None = None
    extra: StructuralExtra = Field(default_factory=StructuralExtra)


"""
class StructBaseSpec(Spec):
    extends: list[str] | None = None
    wrapper: str | None = None
    holder: str | None = None
    properties: list[ExtraProperty] = Field(default_factory=list)
    methods: list[ExtraMethodUnion] = Field(default_factory=list)

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
        logger.debug(f"Normalizing methods: {v}")
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

        logger.debug(f"Normalized methods: {normalized}")
        return normalized
"""


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


# Discriminated Union ensures Pydantic parses the correct subclass instantly based on 'kind'
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


def validate_spec_dict(v: Any) -> Any:
    """Pre-processor to unpack @ syntax in dictionary keys before Pydantic validates."""
    if not isinstance(v, dict):
        return v

    data = {}
    for key, value in v.items():
        if "@" in key and isinstance(value, dict):
            # Work on a copy to avoid mutating the user's original dictionary
            val_copy = value.copy()
            parts = key.split("@")

            if len(parts) >= 2:
                val_copy["kind"] = parts[0]
                val_copy["name"] = parts[1]
            if len(parts) == 3:
                val_copy["signature"] = parts[2]

            data[key] = val_copy
        else:
            data[key] = value

    return data


SpecDict = Annotated[dict[str, SpecUnion], BeforeValidator(validate_spec_dict)]


def create_spec(key: str, **kwargs: Any) -> SpecUnion:
    parts = key.split("@")

    if len(parts) == 2:
        kind, name = parts
        signature = None
    elif len(parts) == 3:
        kind, name, signature = parts
    else:
        logger.error(f"Invalid spec key: {key}")
        raise ValueError(f"Invalid spec key: {key}")

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
    }.get(kind)

    if spec_cls is None:
        logger.error(f"Unknown spec kind: {kind}")
        raise ValueError(f"Unknown spec kind: {kind}")

    return spec_cls(kind=kind, name=name, signature=signature, **kwargs)
