from typing import Any

from loguru import logger

from ...name import Name
from ...node import FunctionPointerType, StructureType, EnumType, BitmaskType, RecordMember
from ..structure_type_renderer import StructureTypeRenderer

SEMANTIC_OPTIONAL_MEMBERS = {
    "DeviceDescriptor.default_queue",
    "FragmentState.constants",
    "ComputeState.constants",
    "DepthStencilState.stencil_front",
    "DepthStencilState.stencil_back",
    "VertexState.constants",
    "VertexState.buffers",
    "RenderPipelineDescriptor.multisample",
    "RenderPipelineDescriptor.primitive",
    "RenderPassColorAttachment.clear_value",
}

SpecialEnums = ["optional bool"]

default_map = {
    "nullptr": "None",
    "true": "True",
    "false": "False",
    #"zero": 0,
    "zero": None,
    "copy stride undefined": 0xFFFFFFFF,
    "limit u32 undefined": 0xFFFFFFFF,
    "limit u64 undefined": 0xFFFFFFFFFFFFFFFF,
    "depth slice undefined": 0xFFFFFFFF,
    "mip level count undefined": 0xFFFFFFFF,
    "array layer count undefined": 0xFFFFFFFF,
    #"depth clear value undefined": float('nan'),
    "depth clear value undefined": None, #TODO: handle float('nan') properly
    "query set index undefined": 0xFFFFFFFF,
    "whole size": 0xFFFFFFFFFFFFFFFF,
}

class StructureTypePyRenderer(StructureTypeRenderer):
    def _implicit_default_for_member(self, member: RecordMember) -> Any:
        # Determine if a member has an implicit default value
        member_type = member.type
        if isinstance(member_type, EnumType) and not member_type.name.get() in SpecialEnums:
            for value in member_type.values:
                if value.value == 0:
                    return f"{member_type.name.CamelCase()}.{self.as_pyEnum(value.name)}"
        elif isinstance(member_type, BitmaskType):
            for value in member_type.values:
                if value.value == 0:
                    return f"{member_type.name.CamelCase()}.{self.as_pyEnum(value.name)}"
        return None

    def render(self):
        node = self.node
        class_name = node.name.CamelCase()
        Out = "Out" if node.output else ""
        '''
        if Out:
            return
        '''
        if not self.is_descriptor_node(node):
            return
        
        self.out / "@dataclass(frozen=True, kw_only=True)" << "\n"
        self.out / f"class {class_name}:" << "\n"
        self.out.indent()

        if node.chained == "in":
            self.out / f"s_type: SType = SType.{self.as_pyEnum(node.name)}" << "\n"

        self.excluded_member_names = {
            member.length_member.name
            for member in node.members
            if member.length_member is not None
        }

        for member in node.members:
            if self.exclude_member(member):
                continue

            member_name = member.name.snake_case()
            member_type = member.type
            member_annotation = member.annotation

            if member_annotation == "const*const*":
                logger.debug(f"Skipping const*const* member {member_name}")
                continue

            # logger.debug(f"member_type: {member_type}")
            if isinstance(member_type, FunctionPointerType):
                logger.debug(f"Skipping function pointer member {member_name}")
                continue

            decoration = self.decorate_member(
                "", self.as_cppType(member_type.name), member
            )
            # print(decoration)
            extra = ""
            if member.optional or f"{class_name}.{member_name}" in SEMANTIC_OPTIONAL_MEMBERS:
                extra = "Optional[Any] = None"
            else:
                extra = "Any"

            member_default = member.default_value

            if member_default is None:
                implicit = self._implicit_default_for_member(member)
                if implicit is not None:
                    member_default = implicit
                    extra += f" = {member_default}"
                # else: leave required (no "= ..."), as before
            else:
            #if member_default is not None:
                if isinstance(member_default, str) and member_default[0].isdigit() and member_default[-1] == 'f':
                    member_default = member_default[:-1]
                if member_default in default_map:
                    member_default = default_map[member_default]
                
                #elif isinstance(member_type, StructureType):
                #    logger.debug(f"Structure member default: {member_default}")
                #    member_default = f"{member_type.name.CamelCase()}()"
                elif isinstance(member_type, EnumType):
                    logger.debug(f"Enum member default: {member_default}")
                    member_default = f"{member_type.name.CamelCase()}.{self.as_pyEnum(Name(member_default))}"
                elif isinstance(member_type, BitmaskType):
                    logger.debug(f"Bitmask member default: {member_default}")
                    member_default = f"{member_type.name.CamelCase()}.{self.as_pyEnum(Name(member_default))}"
                extra += f" = {member_default}"
            (
                self.out
                / f'{member_name}: {extra}  # type: {decoration}, default: {member_default}'
                << "\n"
            )

        if node.name.get() == "surface texture":
            logger.debug(f"surface texture node: {node}")

        self.out.dedent()
        self.out << "\n\n"
