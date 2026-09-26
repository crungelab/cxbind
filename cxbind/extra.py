from typing import Any, Literal, Union
from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from loguru import logger

from .entry import EntryKey

special_methods = {"__init__", "__repr__"}


class Extra(BaseModel):
    pass


class ExtraProperty(BaseModel):
    name: str
    getter: str  # required: a property without a getter can't be bound
    setter: str | None = None


class ExtraMethod(BaseModel):
    kind: str
    name: str
    use: EntryKey | None = None


class ExtraStandardMethod(ExtraMethod):
    kind: Literal["standard"] = "standard"
    use: EntryKey  # required: a standard extra method is always a free function


class ExtraSpecialMethod(ExtraMethod):
    @model_validator(mode="before")
    @classmethod
    def default_name(cls, data: Any) -> Any:
        # The kind *is* the name for special methods (list form has no key).
        if isinstance(data, dict) and "name" not in data:
            data = {**data, "name": data.get("kind")}
        return data

    @model_validator(mode="after")
    def check_name(self) -> "ExtraSpecialMethod":
        if self.name != self.kind:
            raise ValueError(
                f"special method {self.kind!r} can't be named {self.name!r}"
            )
        return self


class ExtraInitMethod(ExtraSpecialMethod):
    kind: Literal["__init__"] = "__init__"
    gen_args: bool = False
    gen_kwargs: bool = False

    @model_validator(mode="after")
    def check_modes(self) -> "ExtraInitMethod":
        if self.gen_args and self.gen_kwargs:
            raise ValueError("__init__: gen_args and gen_kwargs are mutually exclusive")
        if self.gen_args and self.use is not None:
            raise ValueError("__init__: gen_args does not support use")
        return self


class ExtraReprMethod(ExtraSpecialMethod):
    kind: Literal["__repr__"] = "__repr__"
    auto: bool = False


ExtraMethodUnion = Annotated[
    Union[
        ExtraStandardMethod,
        ExtraInitMethod,
        ExtraReprMethod,
    ],
    Field(discriminator="kind"),
]


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
            if not isinstance(item, dict):
                raise ValueError(f"extra property {key!r}: expected a mapping")
            normalized.append({"name": key, **item})
        return normalized

    @field_validator("methods", mode="before")
    @classmethod
    def _normalize_methods(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        normalized = []
        for key, item in v.items():
            if item is None and key in special_methods:
                item = {}  # `__init__:` alone means a plain default init
            elif not isinstance(item, dict):
                raise ValueError(f"extra method {key!r}: expected a mapping")
            item = {"name": key, **item}
            if "kind" not in item:
                item["kind"] = (
                    item["name"] if item["name"] in special_methods else "standard"
                )
            normalized.append(item)
        return normalized