from typing import TYPE_CHECKING, Optional

'''
if TYPE_CHECKING:
    from .project import Project
'''

from typing_extensions import Annotated
from typing import List, Dict, Optional, Any, Literal, Union

from pathlib import Path

from pydantic import BaseModel, Field, BeforeValidator


from loguru import logger
import yaml
from pydantic import Field

from .unit_base import UnitBase

class Unit(UnitBase):
    source: str
    target: str

def validate_unit_dict(v: dict[str, Unit]) -> dict[str, Unit]:
    #logger.debug(f"validate_unit_dict: {v}")
    for key, value in v.items():
        value['name'] = key
    return v

UnitDict = Annotated[dict[str, Unit], BeforeValidator(validate_unit_dict)]