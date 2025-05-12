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


class CppRenderContext(RenderContext):
    def init_render_table(self):
        from .object_type_cpp_renderer import ObjectTypeCppRenderer
        from .structure_type_cpp_renderer import StructureTypeCppRenderer
        from .enum_type_cpp_renderer import EnumTypeCppRenderer
        from .function_declaration_cpp_renderer import FunctionDeclarationCppRenderer

        self.render_table = {
            ObjectType: ObjectTypeCppRenderer,
            StructureType: StructureTypeCppRenderer,
            CallbackInfoType: StructureTypeCppRenderer,
            EnumType: EnumTypeCppRenderer,
            FunctionDeclaration: FunctionDeclarationCppRenderer,
        }
