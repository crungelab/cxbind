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


class PyRenderContext(RenderContext):
    def init_render_table(self):
        from ..renderer import NullRenderer
        from .pyi_object_type_renderer import PyiObjectTypeRenderer
        from .pyi_structure_type_renderer import PyiStructureTypeRenderer
        from .pyi_enum_type_renderer import PyiEnumTypeRenderer
        from .pyi_bitmask_type_renderer import PyiBitmaskTypeRenderer
        from .pyi_function_declaration_renderer import PyiFunctionDeclarationRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: PyiObjectTypeRenderer,
            StructureType: PyiStructureTypeRenderer,
            EnumType: PyiEnumTypeRenderer,
            BitmaskType: PyiBitmaskTypeRenderer,
            FunctionDeclaration: PyiFunctionDeclarationRenderer,
        }
