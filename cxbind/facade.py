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

special_methods = {"__init__", "__repr__"}


class Facade(BaseModel):
    kind: str


class ArgFacade(Facade):
    pass


class VectorArgFacade(ArgFacade):
    kind: Literal["vector"] = "vector"
    length_arg: str


class BufferArgFacade(ArgFacade):
    kind: Literal["buffer"] = "buffer"
    length_arg: str


ArgFacadeUnion = Annotated[
    Union[
        VectorArgFacade,
        BufferArgFacade,
    ],
    Field(discriminator="kind"),
]
