from typing import Type, Any, Dict, List
from clang import cindex
from loguru import logger

from ...node import Node

from . import (
    FunctionRenderer,
    CtorRenderer,
    FieldRenderer,
    MethodRenderer,
    StructRenderer,
    ClassRenderer,
    ClassTemplateRenderer,
    ClassSpecializationRenderer,
    EnumRenderer,
)

NODE_RENDERER_CLS_MAP = {
    "function": FunctionRenderer,
    "ctor": CtorRenderer,
    "field": FieldRenderer,
    "method": MethodRenderer,
    "struct": StructRenderer,
    "class": ClassRenderer,
    "class_template": ClassTemplateRenderer,
    "class_specialization": ClassSpecializationRenderer,
    "enum": EnumRenderer,
}
