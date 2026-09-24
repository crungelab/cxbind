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

    def excluded_params(self) -> set[str]:
        """C++ params this facade consumes, hidden from Python."""
        return set()


class BaseWrapperFacade(Facade):
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
    length_param: str

    def excluded_params(self) -> set[str]:
        return {self.length_param}


class BufferFacade(Facade):
    kind: Literal["buffer"] = "buffer"
    length_param: str

    def excluded_params(self) -> set[str]:
        return {self.length_param}


class CallbackFacade(Facade):
    kind: Literal["callback"] = "callback"
    context_param: str | None = None

    def excluded_params(self) -> set[str]:
        return {self.context_param} if self.context_param else set()


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

WRAPPER_FACADES = {"pycapsule"}
