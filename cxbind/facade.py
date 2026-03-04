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


class WrapperArgFacade(ArgFacade):
    kind: Literal["wrapper"] = "wrapper"
    wrapper: str


class ObjectArgFacade(ArgFacade):
    kind: Literal["object"] = "object"


class VectorArgFacade(ArgFacade):
    kind: Literal["vector"] = "vector"
    length_arg: str


class BufferArgFacade(ArgFacade):
    kind: Literal["buffer"] = "buffer"
    length_arg: str


class CallbackArgFacade(ArgFacade):
    kind: Literal["callback"] = "callback"
    context_arg: str | None = None


ArgFacadeUnion = Annotated[
    Union[
        ObjectArgFacade,
        VectorArgFacade,
        BufferArgFacade,
        CallbackArgFacade,
    ],
    Field(discriminator="kind"),
]
