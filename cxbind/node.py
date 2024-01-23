from typing import List, Dict, Optional, Any

from clang import cindex
from loguru import logger

from .entry import Entry


class Node:
    name: str = None
    first_name: str = None
    pyname: str = None
    cursor: cindex.Cursor = None
    children: list["Node"] = []
    exclude: bool = False
    overload: bool = False
    readonly: bool = False

    def __init__(self, name: str, cursor: cindex.Cursor = None):
        self.name = name
        self.first_name = name.split("::")[-1]
        #if not self.name:
        #    logger.debug(f"name: {name}")
        #    exit()
        self.cursor = cursor
        self.children = []
        self.visited = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, name={self.name}, pyname={self.pyname}>"

    def add_child(self, entry: "Node"):
        self.children.append(entry)


class Function(Node):
    arguments: Dict[str, Any] = {}
    return_type: str = None
    omit_ret: bool = False
    check_result: bool = False


class Ctor(Node):
    pass


class Field(Node):
    pass


class Method(Node):
    pass


class StructBase(Node):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    gen_wrapper: dict = None


class Struct(StructBase):
    pass


class Class(StructBase):
    pass


class Enum(Node):
    pass


class Typedef(Node):
    gen_init: bool = False
    gen_kw_init: bool = False
