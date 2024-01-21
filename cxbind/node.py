from typing import List, Dict, Optional, Any

from clang import cindex
from loguru import logger

from .entry import Entry


class Node:
    fqname: str = None
    name: str = None
    pyname: str = None
    cursor: cindex.Cursor = None
    children: list["Node"] = []
    exclude: bool = False
    overload: bool = False
    readonly: bool = False

    def __init__(self, fqname: str, cursor: cindex.Cursor = None):
        self.fqname = fqname
        self.name = fqname.split("::")[-1]
        #if not self.name:
        #    logger.debug(f"fqname: {fqname}")
        #    exit()
        self.cursor = cursor
        self.children = []
        self.visited = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} fqname={self.fqname}, name={self.name}, pyname={self.pyname}>"

    def add_child(self, entry: "Node"):
        self.children.append(entry)


class FunctionNode(Node):
    arguments: Dict[str, Any] = {}
    return_type: str = None
    omit_ret: bool = False
    check_result: bool = False


class CtorNode(Node):
    pass


class FieldNode(Node):
    pass


class MethodNode(Node):
    pass


class StructOrClassNode(Node):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False
    gen_wrapper: dict = None


class StructNode(StructOrClassNode):
    pass


class ClassNode(StructOrClassNode):
    pass


class EnumNode(Node):
    pass


class EnumConstNode(Node):
    pass


class TypedefNode(Node):
    gen_init: bool = False
    gen_kw_init: bool = False
