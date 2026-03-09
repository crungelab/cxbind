from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union

from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    BeforeValidator,
)
from pydantic_core import core_schema
from loguru import logger


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


class Entry(BaseModel):
    kind: str
    name: str
    signature: str | None = None

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
