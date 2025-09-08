from typing import Type, Any, Dict, List
from clang import cindex
from loguru import logger

from ..node import Node

from . import (
    FunctionBuilder,
    CtorBuilder,
    FieldBuilder,
    MethodBuilder,
    StructBuilder,
    ClassBuilder,
    ClassTemplateBuilder,
    EnumBuilder,
)

NODE_BUILDER_CLS_MAP = {
    "function": FunctionBuilder,
    "ctor": CtorBuilder,
    "field": FieldBuilder,
    "method": MethodBuilder,
    "struct": StructBuilder,
    "class": ClassBuilder,
    "class_template": ClassTemplateBuilder,
    "enum": EnumBuilder,
}
