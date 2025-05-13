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


class HppRenderContext(RenderContext):
    def init_render_table(self):
        from .structure_type_hpp_renderer import StructureTypeHppRenderer
        from .object_type_hpp_renderer import ObjectTypeHppRenderer
        from .enum_type_hpp_renderer import EnumTypeHppRenderer
        from .bitmask_type_hpp_renderer import BitmaskTypeHppRenderer
        from .function_declaration_hpp_renderer import FunctionDeclarationHppRenderer

        self.render_table = {
            StructureType: StructureTypeHppRenderer,
            CallbackInfoType: StructureTypeHppRenderer,
            ObjectType: ObjectTypeHppRenderer,
            EnumType: EnumTypeHppRenderer,
            BitmaskType: BitmaskTypeHppRenderer,
            FunctionDeclaration: FunctionDeclarationHppRenderer,
        }
