from typing import Type, Any, Dict, List
from clang import cindex
from loguru import logger

from .entry import Entry
from .node import Node

from .node_builder import (
    NodeBuilder,
    FunctionNodeBuilder,
    CtorNodeBuilder,
    FieldNodeBuilder,
    MethodNodeBuilder,
    StructNodeBuilder,
    ClassNodeBuilder,
    EnumNodeBuilder,
    TypedefNodeBuilder,
)

NODE_BUILDER_CLS_MAP = {
    "function": FunctionNodeBuilder,
    "ctor": CtorNodeBuilder,
    "field": FieldNodeBuilder,
    "method": MethodNodeBuilder,
    "struct": StructNodeBuilder,
    "class": ClassNodeBuilder,
    "enum": EnumNodeBuilder,
    "typedef": TypedefNodeBuilder,
}
