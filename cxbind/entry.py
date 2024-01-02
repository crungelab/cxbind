from enum import Enum

from clang import cindex

from .context import EntryContext

class EntryKind(Enum):
    FUNCTION = 0
    CTOR = 1
    FIELD = 2
    METHOD = 3
    STRUCT = 4
    CLASS = 5
    ENUM = 6

class Entry:
    context: EntryContext = None
    fqname: str = None
    name: str = None
    pyname: str = None
    config: dict = {}
    node: cindex.Cursor = None
    children: list["Entry"] = []
    exclude: bool = False
    overload: bool = False
    readonly: bool = False

    def __init__(self, context: EntryContext, fqname: str, config: dict={}, node: cindex.Cursor = None):
        self.context = context
        self.fqname = fqname
        self.name = fqname.split('::')[-1]
        self.pyname = self.create_pyname(self.name)
        self.node = node
        self.children = []
        self.configure(config)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} fqname={self.fqname}, name={self.name}, pyname={self.pyname}>'

    def create_pyname(self, name):
        return self.context.format_type(name)

    def configure(self, config):
        #logger.debug(f"config: {config}")
        for key, value in config.items():
            setattr(self, key, value)

    def add_child(self, entry: "Entry"):
        self.children.append(entry)

class FunctionEntry(Entry):
    pass

class CtorEntry(Entry):
    pass

class FieldEntry(Entry):
    def create_pyname(self, name):
        return self.context.format_field(name)

class MethodEntry(Entry):
    pass

class StructOrClassEntry(Entry):
    constructible: bool = True
    has_constructor: bool = False
    gen_init: bool = False
    gen_kw_init: bool = False

class StructEntry(StructOrClassEntry):
    pass

class ClassEntry(StructOrClassEntry):
    pass

class EnumEntry(Entry):
    def create_pyname(self, name):
        return self.context.format_enum(name)

class EnumConstEntry(Entry):
    pass

class TypedefEntry(Entry):
    pass