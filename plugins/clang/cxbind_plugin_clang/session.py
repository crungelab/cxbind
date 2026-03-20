from typing import Optional
from contextvars import ContextVar
import re

from clang import cindex
from loguru import logger

from cxbind import UserSet
from cxbind.spec import Spec
from cxbind.spec_registry import SpecRegistry
from cxbind.unit import Unit

from .node import Node, StructuralNode
#from .node_registry import NodeRegistry

current_session: ContextVar[Optional["Session"]] = ContextVar(
    "current_session", default=None
)


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


class Session:
    def __init__(self, unit: Unit, **kwargs) -> None:
        self.unit = unit
        self.module = unit.module

        self.options = {"save": True}
        self.wrapped: dict[StructuralNode] = {}
        #self.node_registry = NodeRegistry()

        self.target = ""
        self.flags: list[str] = unit.flags.copy()
        self.defaults: dict[str, str] = unit.defaults.copy()
        self.excludes: list[str] = unit.excludes.copy()
        self.specs = unit.specs.copy()

        self.overloads: list[str] = []

        self.node_stack: list[Node] = []
        self.prefixes = unit.prefixes

        self.spec_registry = SpecRegistry()
        for spec in self.specs.values():
            self.register_spec(spec)

        for kw in kwargs:
            if kw == "options":
                options: dict = kwargs[kw]
                options.update(self.options)
                self.options = options

            setattr(self, kw, kwargs[kw])

        self.options = Options(self.options)
        self.excluded = set(self.excludes)
        self.overloaded = Overloaded(self.overloads)

    def make_current(self):
        current_session.set(self)

    @classmethod
    def get_current(cls) -> Optional["Session"]:
        return current_session.get()

    def push_node(self, node) -> None:
        self.node_stack.append(node)

    def pop_node(self) -> Node:
        self.node_stack.pop()

    @property
    def top_node(self) -> Node:
        if len(self.node_stack) == 0:
            return None
        return self.node_stack[-1]

    """
    def register_node(self, node: Node) -> None:
        self.node_registry.register(node)
    """
    
    def register_spec(self, spec: Spec) -> None:
        logger.debug(f"Registering spec: {spec.name}")
        name = spec.name
        key = spec.key
        if spec.exclude:
            logger.debug(f"Excluding: {key}")
            #self.excludes.append(key)
            self.excludes.add(key)
        if spec.overload:
            self.overloads.append(key)
        # TODO: Maybe wrapper should go in Spec proper
        if hasattr(spec, "wrapper") and spec.wrapper:
            logger.debug(f"Adding wrapped: {name}")
            self.wrapped[name] = spec

        self.spec_registry.register(spec)

    def lookup_spec(self, key: str) -> Spec:
        #spec = self.specs.get(key)
        spec = self.spec_registry.get(key)
        logger.debug(f"Looking up spec for key: {key}, specs: {self.specs}, spec: {spec}")
        return spec

    def spell(self, cursor: cindex.Cursor) -> str:
        if cursor is None:
            return ""
        elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ""
        else:
            res = self.spell(cursor.semantic_parent)
            if res != "":
                node = self.top_node
                if node is not None and node.kind != "root":
                    return node.name + "::" + cursor.spelling

                return res + "::" + cursor.spelling
        return cursor.spelling

    @classmethod
    def snake(cls, name: str) -> str:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
        # collapse multiple underscores and strip edges
        return re.sub(r"_+", "_", s2).strip("_").lower()

    @classmethod
    def camel(cls, name: str) -> str:
        s1 = re.sub("(_[a-z])", lambda x: x.group(1)[1].upper(), name)
        return s1[0].upper() + s1[1:]

    def _strip_prefixes(self, text: str, prefixes: list[str]) -> str:
        for prefix in prefixes:
            if (
                text.startswith(prefix)
                and len(text) > len(prefix)
                and (text[len(prefix)].isupper() or text[len(prefix)] == "_")
            ):
                return text[len(prefix) :]
        return text

    def strip_prefixes(self, text: str, prefixes: list[str] = []) -> str:
        return self._strip_prefixes(text, prefixes + self.prefixes)

    def format_field(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = self.snake(name)
        return name

    def format_function(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = self.snake(name)
        name = name.replace(",", "_")
        name = name.replace("<", "_")
        name = name.replace(">", "")
        name = name.replace(" ", "")
        return name

    def format_type(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = name.replace(",", "_")
        name = name.replace("<", "_")
        name = name.replace(">", "")
        name = name.replace(" ", "")
        name = name.rstrip("_")
        name = self.camel(name)
        return name

    def format_enum(self, name: str) -> str:
        name = self.strip_prefixes(name)
        name = self.snake(name).upper()
        name = name.replace("__", "_")
        name = name.rstrip("_")
        return name

    def format_enum_constant(
        self, enum_constant_name: str, enum_name: str = None
    ) -> str:
        # logger.debug(f"format_enum_constant: {enum_constant_name}, {enum_name}")
        name = self.strip_prefixes(enum_constant_name, [enum_name])
        name = self.snake(name).upper()
        name = name.replace("__", "_")
        name = name.lstrip("_")
        name = name.rstrip("_")

        if name.isdigit():
            # if name.isnumeric():
            # name = f"_{name}"
            name = self.strip_prefixes(enum_constant_name).upper()

        return name
