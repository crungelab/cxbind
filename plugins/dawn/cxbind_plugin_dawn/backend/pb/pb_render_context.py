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


class PbRenderContext(RenderContext):
    def init_render_table(self):
        from ..renderer import NullRenderer
        from .object_type_pb_renderer import ObjectTypePbRenderer
        from .structure_type_pb_renderer import StructureTypePbRenderer
        from .enum_type_pb_renderer import EnumTypePbRenderer
        from .bitmask_type_pb_renderer import BitmaskTypePbRenderer
        from .function_declaration_pb_renderer import FunctionDeclarationPbRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: ObjectTypePbRenderer,
            StructureType: StructureTypePbRenderer,
            EnumType: EnumTypePbRenderer,
            BitmaskType: BitmaskTypePbRenderer,
            FunctionDeclaration: FunctionDeclarationPbRenderer,
        }
