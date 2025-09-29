from typing_extensions import Annotated
from typing import List, Dict, Optional, Any, Literal, Union

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict, field_validator, model_validator

from loguru import logger


class Facade(BaseModel):
    kind: str
