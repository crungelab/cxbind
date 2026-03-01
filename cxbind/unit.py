from typing_extensions import Annotated
from typing import List, Dict, Optional, Any, Literal, Union

from pydantic import BaseModel, Field, BeforeValidator, model_validator, field_validator


from loguru import logger
from pydantic import Field

from .unit_base import UnitBase
from .transform import Transform, _registry as TRANSFORM_REGISTRY


class Unit(UnitBase):
    source: Optional[str] = None
    sources: Optional[List[str]] = []
    #target: str
    target: Optional[str] = None
    template: Optional[str] = None
    mapped: Optional[List[str]] = []
    transforms: list[Transform] = []
    generate: bool = True
    internal: bool = False

    # Copilot suggested fields, but they are not used in the current implementation. They can be added later if needed.
    #overwrite: bool = False
    #rename: Optional[str] = None
    #doc: Optional[str] = None
    #extra: Optional[dict[str, Any]] = None

    @model_validator(mode='after')
    def handle_internal_logic(self) -> 'Unit':
        if self.internal:
            self.generate = False
        return self

    @field_validator("transforms", mode="before")
    @classmethod
    def dispatch_transforms(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise TypeError("transforms must be a list")

        out = []
        for i, raw in enumerate(v):
            logger.debug(f"dispatch_transforms: raw[{i}] = {raw}")
            if isinstance(raw, Transform):
                out.append(raw)
                continue
            if not isinstance(raw, dict):
                raise TypeError(f"transforms[{i}] must be an object/dict")

            t = raw.get("name")
            model_cls = TRANSFORM_REGISTRY.get(t)
            if model_cls is None:
                raise ValueError(f"Unknown name {t!r} at transforms[{i}]")

            out.append(model_cls.model_validate(raw))
        return out

def validate_unit_dict(v: dict[str, Unit]) -> dict[str, Unit]:
    #logger.debug(f"validate_unit_dict: {v}")
    for key, value in v.items():
        value['name'] = key
    return v

UnitDict = Annotated[dict[str, Unit], BeforeValidator(validate_unit_dict)]