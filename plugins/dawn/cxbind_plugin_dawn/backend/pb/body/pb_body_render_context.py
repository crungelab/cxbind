from ...render_context import RenderContext

from ....node import (
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
        from ...renderer import NullRenderer
        from .object_type_pb_body_renderer import ObjectTypePbBodyRenderer
        from .structure_type_pb_body_renderer import StructureTypePbBodyRenderer
        from .enum_type_pb_body_renderer import EnumTypePbBodyRenderer
        from .bitmask_type_pb_body_renderer import BitmaskTypePbBodyRenderer
        from .function_declaration_pb_body_renderer import FunctionDeclarationPbBodyRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: ObjectTypePbBodyRenderer,
            StructureType: StructureTypePbBodyRenderer,
            EnumType: EnumTypePbBodyRenderer,
            BitmaskType: BitmaskTypePbBodyRenderer,
            FunctionDeclaration: FunctionDeclarationPbBodyRenderer,
        }
