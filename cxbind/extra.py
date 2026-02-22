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

class ExtraProperty(BaseModel):
    name: str
    getter: str | None = None
    setter: str | None = None


class ExtraMethod(BaseModel):
    kind: str
    name: str
    use: str | None = None
    gen_args: bool | None = False
    gen_kwargs: bool | None = False


class ExtraStandardMethod(ExtraMethod):
    kind: Literal["standard"] = "standard"

class ExtraSpecialMethod(ExtraMethod):
    pass

class ExtraInitMethod(ExtraSpecialMethod):
    kind: Literal["__init__"] = "__init__"


class ExtraReprMethod(ExtraSpecialMethod):
    kind: Literal["__repr__"] = "__repr__"


ExtraMethodUnion = Annotated[
    Union[
        ExtraStandardMethod,
        ExtraInitMethod,
        ExtraReprMethod,
    ],
    Field(discriminator="kind"),
]
