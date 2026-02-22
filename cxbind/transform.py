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


_registry: dict[str, type["Transform"]] = {}

def register_transform(name: str):
    def decorator(cls: type["Transform"]) -> type["Transform"]:
        _registry[name] = cls
        return cls
    return decorator


class Transform(BaseModel):
    name: str
