from typing import TYPE_CHECKING, Type, Dict, List, Any, Callable

if TYPE_CHECKING:
    from cxbind.node_builder import NodeBuilder


import re
from contextlib import contextmanager
from . import UserSet

from clang import cindex
from loguru import logger

from .node import Node
from .entry import Entry
from .generator_config import GeneratorConfig


#TODO: Use pydantic settings
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
    def __init__(self, config: GeneratorConfig, **kwargs) -> None:
        self.options = { 'save': True }
        self.prefixes = None
        self.wrapped: Dict[Entry] = {}

        self.indentation = 0
        self.text = ""
        self.source = ""
        self.mapped: List[str] = []  # headers we want to generate bindings for
        self.target = ""
        self.module = ""
        self.flags: List[str] = []
        self.defaults: Dict[str, str] = {}
        self.excludes: List[str] = []
        self.overloads: List[str] = []

        self.entries: Dict[str, Entry] = {}

        self.nodes: Dict[str, Node] = {}
        self.node_stack: List[Node] = []

        for attr in vars(config):
            setattr(self, attr, getattr(config, attr))

        for entry in config.function:
            self.register_entry(entry)
        for entry in config.method:
            self.register_entry(entry)
        for entry in config.struct:
            self.register_entry(entry)
        for entry in config.cls:
            self.register_entry(entry)
        for entry in config.field:
            self.register_entry(entry)

        for key in kwargs:
            if key == 'options':
                options: Dict = kwargs[key]
                options.update(self.options)
                self.options = options

            setattr(self, key, kwargs[key])
        
        self.options = Options(self.options)
        self.excluded = set(self.excludes)
        self.overloaded = Overloaded(self.overloads)

    def write(self, text: str):
        self.text += text

    def write_indented(self, text: str):
        self.write(" " * self.indentation * 4)
        self.write(text)

    def __call__(self, line=""):
        if len(line):
            line = line.replace(">>", "> >")
            self.write_indented(line)
        self.write("\n")

    @contextmanager
    def enter(self, node):
        self.push_node(node)
        self.indent()
        yield node
        self.dedent()
        self.pop_node()

    def __enter__(self):
        self.indent()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()

    def push_node(self, node):
        self.node_stack.append(node)

    def pop_node(self):
        self.node_stack.pop()

    def indent(self):
        self.indentation += 1

    def dedent(self):
        self.indentation -= 1

    @property
    def top_node(self):
        if len(self.node_stack) == 0:
            return None
        return self.node_stack[-1]

    def register_entry(self, entry: Entry):
        logger.debug(f"Registering {entry}")
        fqname = entry.fqname
        if entry.exclude:
            self.excludes.append(fqname)
        if entry.overload:
            self.overloads.append(fqname)
        if hasattr(entry, "gen_wrapper") and entry.gen_wrapper:
            logger.debug(f"Adding wrapped {fqname}")
            self.wrapped[fqname] = entry

        self.entries[fqname] = entry

        return entry

    def lookup_entry(self, key: str) -> Entry:
        #logger.debug(f"Looking up {entry_key}")
        if key in self.entries:
            return self.entries[key]
        return None

    def lookup_node(self, key: str) -> Node:
        #logger.debug(f"Looking up {entry_key}")
        if key in self.nodes:
            return self.nodes[key]
        return None

    def create_builder(self, entry_key: str, cursor: cindex.Cursor = None) -> "NodeBuilder":
        from .node_builder.node_builder_cls_map import NODE_BUILDER_CLS_MAP
        from .node_builder import NodeBuilder
        kind, fqname = entry_key.split(".")
        builder_cls: Type[NodeBuilder] = NODE_BUILDER_CLS_MAP[kind]
        entry = self.lookup_entry(fqname)
        builder = builder_cls(self, fqname, cursor, entry)
        return builder

    @classmethod
    def spell(cls, node: cindex.Cursor):
        if node is None:
            return ""
        elif node.kind == cindex.CursorKind.TRANSLATION_UNIT:
            return ""
        else:
            res = cls.spell(node.semantic_parent)
            if res != "":
                return res + "::" + node.spelling
        return node.spelling

    @classmethod
    def snake(cls, name: str):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z])([A-Z])", r"\1_\2", s1).lower()

    def strip_prefixes(self, name: str):
        # logger.debug(f"prefixes: {self.prefixes}")
        if isinstance(self.prefixes, str):
            name = name.replace(self.prefixes, "", 1)
        elif isinstance(self.prefixes, list):
            for prefix in self.prefixes:
                name = name.replace(prefix, "", 1)
        return name

    def format_field(self, name: str):
        name = self.strip_prefixes(name)
        name = self.snake(name)
        name = name.rstrip("_")
        name = name.replace("__", "_")
        return name

    def format_type(self, name: str):
        name = self.strip_prefixes(name)
        name = name.replace("<", "_")
        name = name.replace(">", "")
        name = name.replace(" ", "")
        name = name.rstrip("_")
        return name

    def format_enum(self, name: str):
        name = self.strip_prefixes(name)
        name = self.snake(name).upper()
        name = name.replace("__", "_")
        name = name.rstrip("_")
        return name

    def arg_type(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"std::array<{argument.type.get_array_element_type().spelling}, {argument.type.get_array_size()}>&"

        type_name = argument.type.spelling.split(" ")[0]
        if type_name in self.wrapped:
            return argument.type.spelling.replace(
                type_name, self.wrapped[type_name].gen_wrapper["type"]
            )

        return argument.type.spelling

    def arg_name(self, argument):
        if argument.type.kind == cindex.TypeKind.CONSTANTARRAY:
            return f"&{argument.spelling}[0]"
        return argument.spelling

    def arg_types(self, arguments):
        return ", ".join([self.arg_type(a) for a in arguments])

    def arg_names(self, arguments: List[cindex.Cursor]):
        returned = []
        for a in arguments:
            type_name = a.type.spelling.split(" ")[0]
            if type_name in self.wrapped:
                returned.append(f"{self.arg_name(a)}->get()")
            else:
                returned.append(self.arg_name(a))
        return ", ".join(returned)

    """
    def arg_names(self, arguments):
        return ', '.join([self.arg_name(a) for a in arguments])
    """

    def arg_string(self, arguments):
        return ", ".join(
            ["{} {}".format(self.arg_type(a), a.spelling) for a in arguments]
        )
