from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

if TYPE_CHECKING:
    from .node_builder import NodeBuilder

import re
from contextlib import contextmanager

from clang import cindex
from loguru import logger

from cxbind import UserSet
from cxbind.spec import Spec
from cxbind.unit import Unit
from cxbind.code_stream import CodeStream

from .node import Node, StructBaseNode


# TODO: Use pydantic settings
class Options:
    def __init__(self, *options, **kwargs):
        for dictionary in options:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Overloaded(UserSet):
    def __init__(self, data) -> None:
        super().__init__(data)
        self.visited = set()

    def is_overloaded(self, cursor):
        return self.name(cursor) in self


class BuilderContext:
    def __init__(self, unit: Unit, **kwargs) -> None:
        self.unit = unit

        self.options = {"save": True}
        self.wrapped: Dict[StructBaseNode] = {}
        self.visited: Dict[Node] = {}
        self.chaining = False

        self.out = CodeStream()

        self.module = unit.module

        self.mapped: List[str] = unit.mapped.copy()
        self.target = ""
        self.flags: List[str] = unit.flags.copy()
        self.defaults: Dict[str, str] = {}
        self.excludes: List[str] = unit.excludes.copy()
        self.overloads: List[str] = []

        self.specs = unit.specs.copy()
        self.node_stack: List[Node] = []
        self.prefixes = unit.prefixes

        for name, spec in self.specs.items():
            self.register_spec(spec)

        for key in kwargs:
            if key == "options":
                options: Dict = kwargs[key]
                options.update(self.options)
                self.options = options

            setattr(self, key, kwargs[key])

        self.options = Options(self.options)
        self.excluded = set(self.excludes)
        self.overloaded = Overloaded(self.overloads)

    def push_node(self, node) -> None:
        self.node_stack.append(node)

    def pop_node(self) -> Node:
        self.node_stack.pop()

    @property
    def top_node(self) -> Node:
        if len(self.node_stack) == 0:
            return None
        return self.node_stack[-1]

    def register_spec(self, spec: Spec) -> None:
        logger.debug(f"Registering spec: {spec.name}")
        name = spec.name
        key = spec.key
        if spec.exclude:
            logger.debug(f"Excluding: {key}")
            self.excludes.append(key)
        if spec.overload:
            self.overloads.append(key)
        if hasattr(spec, "wrapper") and spec.wrapper:
            logger.debug(f"Adding wrapped: {name}")
            self.wrapped[name] = spec

    def lookup_spec(self, key: str) -> Spec:
        spec = self.specs.get(key)
        return spec

    def create_builder(
        self, entry_key: str, cursor: cindex.Cursor = None
    ) -> "NodeBuilder":
        from .node_builder.node_builder_cls_map import NODE_BUILDER_CLS_MAP
        from .node_builder import NodeBuilder

        kind, name = entry_key.split("/")
        builder_cls: Type[NodeBuilder] = NODE_BUILDER_CLS_MAP[kind]
        builder = builder_cls(self, name, cursor)
        return builder

    def spell(self, cursor: cindex.Cursor) -> str:
        if cursor is None:
            return ""
        elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ""
        else:
            res = self.spell(cursor.semantic_parent)
            if res != "":
                node = self.top_node
                if node is not None:
                    return node.name + "::" + cursor.spelling

                return res + "::" + cursor.spelling
        return cursor.spelling

    @classmethod
    def snake(cls, name: str) -> str:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z])([A-Z])", r"\1_\2", s1).lower()

    def _strip_prefixes(self, text: str, prefixes: List[str]) -> str:
        for prefix in prefixes:
            if (
                text.startswith(prefix)
                and len(text) > len(prefix)
                and text[len(prefix)].isupper()
            ):
                return text[len(prefix) :]
        return text

    def strip_prefixes(self, text: str, prefixes: List[str] = []) -> str:
        return self._strip_prefixes(text, prefixes + self.prefixes)

    def format_field(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = self.snake(name)
        name = name.rstrip("_")
        name = name.replace("__", "_")
        return name

    def format_type(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = name.replace(",", "_")
        name = name.replace("<", "_")
        name = name.replace(">", "")
        name = name.replace(" ", "")
        name = name.rstrip("_")
        return name

    def format_enum(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = self.snake(name).upper()
        name = name.replace("__", "_")
        name = name.rstrip("_")
        return name

    def format_enum_constant(self, name: str, enum_name: str = None) -> str:
        name = self.strip_prefixes(name, [enum_name])
        name = self.snake(name).upper()
        name = name.replace("__", "_")
        name = name.rstrip("_")
        return name
