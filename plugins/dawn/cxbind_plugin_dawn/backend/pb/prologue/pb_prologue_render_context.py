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


class PbPrologueRenderContext(RenderContext):
    def init_render_table(self):
        from ...renderer import NullRenderer
        from .pb_prologue_object_type_renderer import PbPrologueObjectTypeRenderer
        from .pb_prologue_structure_type_renderer import PbPrologueStructureTypeRenderer
        from .pb_prologue_enum_type_renderer import PbPrologueEnumTypeRenderer
        from .pb_prologue_bitmask_type_renderer import PbPrologueBitmaskTypeRenderer
        from .pb_prologue_function_declaration_renderer import PbPrologueFunctionDeclarationRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: PbPrologueObjectTypeRenderer,
            StructureType: PbPrologueStructureTypeRenderer,
            EnumType: PbPrologueEnumTypeRenderer,
            BitmaskType: PbPrologueBitmaskTypeRenderer,
            FunctionDeclaration: PbPrologueFunctionDeclarationRenderer,
        }
