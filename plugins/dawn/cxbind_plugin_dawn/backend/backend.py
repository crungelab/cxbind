from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ..program import Program

from pathlib import Path

from loguru import logger
import jinja2

from ..processor import Processor
from ..node import (
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
from ..name import Name

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
        for method in obj.methods:
            method.return_type = self.program.lookup(method.return_type_ref) or self.program.lookup("void")
            args_by_name = {arg.name: arg for arg in method.args}
            for arg in method.args:
                arg.type = self.program.lookup(arg.type_ref)
                if arg.length is not None and isinstance(arg.length, str):
                    arg.length_member = args_by_name[Name.intern(arg.length)]

        self.object_types.append(obj)

    def process_enum_type(self, enum: EnumType):
        # logger.debug(f"Backend: Processing enum type '{enum.name.CamelCase()}'")
        self.enum_types.append(enum)

    def process_bitmask_type(self, bitmask: BitmaskType):
        # logger.debug(f"Backend: Processing bitmask type '{bitmask.name.CamelCase()}'")
        self.bitmask_types.append(bitmask)

    def process_structure_type(self, structure: StructureType):
        # logger.debug(f"Backend: Processing structure type '{structure.name.CamelCase()}'")
        members_by_name = {member.name: member for member in structure.members}
        for member in structure.members:
            member.type = self.program.lookup(member.type_ref)
            if member.length is not None and isinstance(member.length, str):
                member.length_member = members_by_name[Name.intern(member.length)]

        self.structure_types.append(structure)

    def process_function_pointer_type(self, function_pointer: FunctionPointerType):
        logger.debug(
            f"Backend: Processing function pointer type '{function_pointer.name.CamelCase()}, category: {function_pointer.category}, class:{function_pointer.__class__.__name__}'"
        )
        self.function_pointer_types.append(function_pointer)

    def process_constant_definition(self, constant: ConstantDefinition):
        # logger.debug(f"Backend: Processing constant definition '{constant.name.CamelCase()}'")
        constant.type = self.program.lookup(constant.type_ref)
        self.constant_definitions.append(constant)

    def process_function_declaration(self, fn_decl: FunctionDeclaration):
        # logger.debug(f"Backend: Processing function declaration '{fn_decl.name.CamelCase()}'")
        fn_decl.return_type = self.program.lookup(fn_decl.return_type_ref) or self.program.lookup("void")
        args_by_name = {arg.name: arg for arg in fn_decl.args}
        for arg in fn_decl.args:
            arg.type = self.program.lookup(arg.type_ref)
            if arg.length is not None and isinstance(arg.length, str):
                arg.length_member = args_by_name[Name.intern(arg.length)]

        self.function_declarations.append(fn_decl)

    def process_callback_info_type(self, callback_info: CallbackInfoType):
        # logger.debug(f"Backend: Processing callback info type '{callback_info.name.CamelCase()}'")
        members_by_name = {member.name: member for member in callback_info.members}
        for member in callback_info.members:
            member.type = self.program.lookup(member.type_ref)
            if member.length is not None and isinstance(member.length, str):
                member.length_member = members_by_name[Name.intern(member.length)]

        self.callback_info_types.append(callback_info)

    def process_callback_function_type(self, callback_function: CallbackFunctionType):
        logger.debug(
            f"Backend: Processing callback function type '{callback_function.name.CamelCase()}'"
        )
        self.callback_function_types.append(callback_function)
