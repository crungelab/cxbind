from ..render_context import RenderContext

from ...node import (
    ObjectType,
    EnumType,
    BitmaskType,
    StructureType,
    CallbackInfoType,
    CallbackFunctionType,
    FunctionDeclaration,
)


class PbBodyRenderContext(RenderContext):
    def init_render_table(self):
        from ..renderer import NullRenderer
        from .pb_object_type_renderer import PbObjectTypeRenderer
        from .pb_structure_type_renderer import PbStructureTypeRenderer
        from .pb_enum_type_renderer import PbEnumTypeRenderer
        from .pb_bitmask_type_renderer import PbBitmaskTypeRenderer
        from .pb_function_declaration_renderer import PbFunctionDeclarationRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: PbObjectTypeRenderer,
            StructureType: PbStructureTypeRenderer,
            EnumType: PbEnumTypeRenderer,
            BitmaskType: PbBitmaskTypeRenderer,
            FunctionDeclaration: PbFunctionDeclarationRenderer,
        }
