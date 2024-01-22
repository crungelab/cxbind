from typing import Type, Any, Dict, List
from clang import cindex
from loguru import logger

from .entry import Entry
from .node import Function, Ctor, Field, Method, Struct, Class, Enum, Typedef

from . import (
    Function,
    Ctor,
    Field,
    Method,
    Struct,
    Class,
    Enum,
    Typedef,
)

NODE_CLS_MAP = {
    "function": Function,
    "ctor": Ctor,
    "field": Field,
    "method": Method,
    "struct": Struct,
    "class": Class,
    "enum": Enum,
    "typedef": Typedef,
}
