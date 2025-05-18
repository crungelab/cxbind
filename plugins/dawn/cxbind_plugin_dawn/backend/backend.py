from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ..program import Program

from pathlib import Path

from loguru import logger
import jinja2
import os

from ..processor import Processor
from ..node import (
    Root,
    ObjectType,
    EnumType,
    BitmaskType,
    StructureType,
    NativeType,
    FunctionPointerType,
    ConstantDefinition,
    FunctionDeclaration,
    CallbackInfoType,
    CallbackFunctionType,
)


class Backend(Processor):
    def __init__(self, program: "Program") -> None:
        super().__init__(program)
        self.native_types: List[NativeType] = []
        self.object_types: List[ObjectType] = []
        self.enum_types: List[EnumType] = []
        self.bitmask_types: List[BitmaskType] = []
        self.structure_types: List[StructureType] = []
        self.function_pointer_types: List[FunctionPointerType] = []
        self.constant_definitions: List[ConstantDefinition] = []
        self.function_declarations: List[FunctionDeclaration] = []
        self.callback_info_types: List[CallbackInfoType] = []
        self.callback_function_types: List[CallbackFunctionType] = []

        CWD_PATH = Path(".")
        BASE_PATH = Path(__file__).parent.parent

        config_searchpath = CWD_PATH / ".cxbind" / "templates"
        default_searchpath = BASE_PATH / "templates"
        searchpath = [config_searchpath, default_searchpath]

        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

    def run(self):
        self.process()
        self.render()

    def render(self):
        pass

    def process(self):
        for key, entry in self.program.root:
            # logger.debug(f"Backend: Processing '{key}': {entry.__class__.__name__}")
            if isinstance(entry, ObjectType):
                self.process_object_type(entry)
            elif isinstance(entry, NativeType):
                self.process_native_type(entry)
            elif isinstance(entry, EnumType):
                self.process_enum_type(entry)
            elif isinstance(entry, BitmaskType):
                self.process_bitmask_type(entry)
            elif isinstance(entry, StructureType):
                self.process_structure_type(entry)
            elif isinstance(entry, FunctionPointerType):
                self.process_function_pointer_type(entry)
            elif isinstance(entry, ConstantDefinition):
                self.process_constant_definition(entry)
            elif isinstance(entry, FunctionDeclaration):
                self.process_function_declaration(entry)
            elif isinstance(entry, CallbackInfoType):
                self.process_callback_info_type(entry)
            elif isinstance(entry, CallbackFunctionType):
                self.process_callback_function_type(entry)
            else:
                logger.debug(f"Backend: Found unknown type '{key}'")

    def process_native_type(self, native: NativeType):
        # logger.debug(f"Backend: Processing native type '{native.name.CamelCase()}'")
        self.native_types.append(native)

    def process_object_type(self, obj: ObjectType):
        # logger.debug(f"Backend: Processing object type '{obj.name.CamelCase()}'")
        self.object_types.append(obj)

    def process_enum_type(self, enum: EnumType):
        # logger.debug(f"Backend: Processing enum type '{enum.name.CamelCase()}'")
        self.enum_types.append(enum)

    def process_bitmask_type(self, bitmask: BitmaskType):
        # logger.debug(f"Backend: Processing bitmask type '{bitmask.name.CamelCase()}'")
        self.bitmask_types.append(bitmask)

    def process_structure_type(self, structure: StructureType):
        logger.debug(f"Backend: Processing structure type '{structure.name.CamelCase()}'")
        self.structure_types.append(structure)

    def process_function_pointer_type(self, function_pointer: FunctionPointerType):
        logger.debug(
            f"Backend: Processing function pointer type '{function_pointer.name.CamelCase()}, category: {function_pointer.category}, class:{function_pointer.__class__.__name__}'"
        )
        self.function_pointer_types.append(function_pointer)

    def process_constant_definition(self, constant: ConstantDefinition):
        # logger.debug(f"Backend: Processing constant definition '{constant.name.CamelCase()}'")
        self.constant_definitions.append(constant)

    def process_function_declaration(self, fn_decl: FunctionDeclaration):
        # logger.debug(f"Backend: Processing function declaration '{fn_decl.name.CamelCase()}'")
        self.function_declarations.append(fn_decl)

    def process_callback_info_type(self, callback_info: CallbackInfoType):
        # logger.debug(f"Backend: Processing callback info type '{callback_info.name.CamelCase()}'")
        self.callback_info_types.append(callback_info)

    def process_callback_function_type(self, callback_function: CallbackFunctionType):
        logger.debug(
            f"Backend: Processing callback function type '{callback_function.name.CamelCase()}'"
        )
        self.callback_function_types.append(callback_function)
