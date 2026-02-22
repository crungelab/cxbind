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


TRANSFORM_REGISTRY: dict[str, type["Transform"]] = {}


class Transform(BaseModel):
    name: str
