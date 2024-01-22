from typing import Type, Any, Dict, List
from clang import cindex
from loguru import logger

from ..entry import Entry
from ..node import Node

from . import (
    FunctionBuilder,
    CtorBuilder,
    FieldBuilder,
    MethodBuilder,
    StructBuilder,
    ClassBuilder,
    EnumBuilder,
    TypedefBuilder,
)

NODE_BUILDER_CLS_MAP = {
    "function": FunctionBuilder,
    "ctor": CtorBuilder,
    "field": FieldBuilder,
    "method": MethodBuilder,
    "struct": StructBuilder,
    "class": ClassBuilder,
    "enum": EnumBuilder,
    "typedef": TypedefBuilder,
}
