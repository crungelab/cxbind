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


class BaseWrapperFacade(Facade):
    #kind: Literal["base_wrapper"] = "base_wrapper"
    pass


class PyCapsuleFacade(BaseWrapperFacade):
    kind: Literal["pycapsule"] = "pycapsule"


class WrapperFacade(BaseWrapperFacade):
    kind: Literal["wrapper"] = "wrapper"
    wrapper: str


class ObjectFacade(Facade):
    kind: Literal["object"] = "object"


class VectorFacade(Facade):
    kind: Literal["vector"] = "vector"
    length_arg: str


class BufferFacade(Facade):
    kind: Literal["buffer"] = "buffer"
    length_arg: str


class CallbackFacade(Facade):
    kind: Literal["callback"] = "callback"
    context_arg: str | None = None


FacadeUnion = Annotated[
    Union[
        PyCapsuleFacade,
        WrapperFacade,
        ObjectFacade,
        VectorFacade,
        BufferFacade,
        CallbackFacade,
    ],
    Field(discriminator="kind"),
]

WRAPPER_FACADES = {
    "pycapsule"
}