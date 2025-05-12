from typing import List, Optional, Dict, Union, Literal, Annotated, Any
from pydantic import BaseModel, Field, ValidationError, RootModel, ConfigDict

from .name import Name


class Node(BaseModel):
    tags: Optional[List[str]] = None
    _comment: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed = True)


class RecordMember(Node):
    name: Name
    type: str
    annotation: Optional[str] = None
    optional: Optional[bool] = False
    no_default: Optional[bool] = False
    default_value: Union[str, int] = Field(alias="default", default=None)
    length: Optional[Union[str, int]] = None


class Method(Node):
    name: Name
    returns: Optional[str] = None
    args: Optional[List[RecordMember]] = None
    no_autolock: Optional[bool] = Field(alias="no autolock", default=None)


class EnumValue(Node):
    name: Name
    value: int


class BitmaskValue(Node):
    name: Name
    value: int

class Entry(Node):
    category: str
    name: Optional[Name] = None
    
    def __hash__(self):
        return hash(self.name)


class TypeDefinition(Entry):
    category: Literal["typedef"]
    type: Optional[str]


class EnumType(Entry):
    category: Literal["enum"]
    values: List[EnumValue]
    emscripten_no_enum_table: Optional[bool] = False


class BitmaskType(Entry):
    category: Literal["bitmask"]
    values: List[BitmaskValue]


class ObjectType(Entry):
    category: Literal["object"] = "object"
    methods: Optional[List[Method]] = []
    no_autolock: Optional[bool] = Field(alias="no autolock", default=None)


class StructureBase(Entry):
    members: List[RecordMember]

class StructureType(StructureBase):
    category: Literal["structure"]
    extensible: Optional[Union[str, bool]] = None
    chained: Optional[str] = None
    chain_roots: Optional[List[str]] = Field(alias="chain roots", default=None)
    extensions: Optional[List[Any]] = Field(None, exclude=True, repr=False)
    out: Optional[bool] = False

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        # Chained structs inherit from pywgpu::ChainedStruct, which has
        # nextInChain, so setting both extensible and chained would result in
        # two nextInChain members.
        assert not (self.extensible and self.chained)

        if self.chained:
            assert self.chained == "in" or self.chained == "out"
            #assert self.chain_roots # See "dawn injected invalid s type"
            self.add_next_in_chain()

        if self.extensible:
            assert self.extensible == "in" or self.extensible == "out"
            self.add_next_in_chain()
        # self.extensions = []

    def add_next_in_chain(self):
        self.members.insert(
            0,
            RecordMember(
                name=Name.intern("next in chain"),
                #type="const void*",
                #type="chained struct",
                type="chained struct" if not self.output else "chained struct out",
                #annotation="value",
                #annotation="const*",
                annotation="const*" if not self.output else "*",
                optional=True,
            ),
        )

    '''
    @property
    def output(self):
        # self.out is a temporary way to express that this is an output structure
        # without also making it extensible. See
        # https://dawn-review.googlesource.com/c/dawn/+/212174/comment/2271690b_1fd82ea9/

        if self.name and self.name.canonical_case() == "instance capabilities":
            return False

        return self.chained == "out" or self.extensible == "out" or self.out
    '''
    @property
    def output(self):
        return self.chained == "out" or self.extensible == "out"

    '''
    @property
    def has_free_members_function(self):
        if not self.output:
            return False
        for m in self.members:
            if m.annotation != 'value' \
                or m.type.name.canonical_case() == 'string view':
                return True
        return False
    '''

    @property
    def has_free_members_function(self):
        if not self.output:
            return False
        for m in self.members:
            #if m.annotation != "value":
            if m.annotation is not None:
                return True
        return False


class CallbackInfoType(StructureBase):
    category: Literal["callback info"]


class NativeType(Entry):
    category: Literal["native"]
    wasm_type: Optional[str] = Field(alias="wasm type", default=None)


class FunctionPointerType(Entry):
    category: Literal["function pointer"]
    returns: Optional[str] = None
    args: Optional[List[RecordMember]] = None


class CallbackFunctionType(Entry):
    category: Literal["callback function"]
    args: Optional[List[RecordMember]] = None


class ConstantDefinition(Entry):
    category: Literal["constant"]
    type: str
    value: str
    cpp_value: Optional[str] = None


class FunctionDeclaration(Entry):
    category: Literal["function"]
    returns: Optional[str] = None
    args: Optional[List[RecordMember]] = None


TypeUnion = Annotated[
    Union[
        ObjectType,
        TypeDefinition,
        EnumType,
        BitmaskType,
        StructureType,
        NativeType,
        FunctionPointerType,
        ConstantDefinition,
        FunctionDeclaration,
        CallbackInfoType,
        CallbackFunctionType,
    ],
    Field(discriminator="category")
]

class Category:
    NATIVE = "native"
    OBJECT = "object"
    ENUM = "enum"
    BITMASK = "bitmask"
    STRUCTURE = "structure"
    FUNCTION_POINTER = "function pointer"
    CONSTANT = "constant"
    FUNCTION = "function"
    CALLBACK_INFO = "callback info"
    CALLBACK_FUNCTION = "callback function"

    def __init__(self):
        self.entries = {}

    def add_entry(self, entry):
        self.entries[entry.name] = entry

    def find_entry(self, name):
        return self.entries.get(name)

class Catalog:
    def __init__(self):
        self.categories = {
            Category.NATIVE: Category(),
            Category.OBJECT: Category(),
            Category.ENUM: Category(),
            Category.BITMASK: Category(),
            Category.STRUCTURE: Category(),
            Category.FUNCTION_POINTER: Category(),
            Category.CONSTANT: Category(),
            Category.FUNCTION: Category(),
            Category.CALLBACK_INFO: Category(),
            Category.CALLBACK_FUNCTION: Category(),
        }

    def add_entry(self, entry):
        if entry.category in self.categories:
            self.categories[entry.category].add_entry(entry)


class Root(RootModel):
    root: Dict[str, TypeUnion] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    def __init__(self, **data):
        super().__init__(**data)
        for key, value in self.root.items():
            native = isinstance(value, NativeType)
            value.name = Name.intern(key, native=native)

        self.root["instance capabilities"].extensible = "in"
        self.root["surface texture"].extensible = "in"
        self.root["adapter info"].extensible = "in"

        self.root["chained struct"] = StructureType(
            name=Name.intern("chained struct"),
            category="structure",
            members=[
                RecordMember(
                    name=Name.intern("next_in_chain"),
                    #type="const void*",
                    type="chained struct",
                    #annotation="value",
                    annotation="const*",
                    #optional=True,
                )
            ],
        )

        self.root["chained struct out"] = StructureType(
            name=Name.intern("chained struct out"),
            category="structure",
            members=[
                RecordMember(
                    name=Name.intern("next_in_chain"),
                    #type="const void*",
                    type="chained struct out",
                    #annotation="value",
                    annotation="const*",
                    #optional=True,
                )
            ],
        )

    def __iter__(self):
        return iter(self.root.items())

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, value):
        self.root[key] = value

    def __delitem__(self, key):
        del self.root[key]

    def __len__(self):
        return len(self.root)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
