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
        from .object_type_py_renderer import ObjectTypePyRenderer
        from .structure_type_py_renderer import StructureTypePyRenderer
        from .enum_type_py_renderer import EnumTypePyRenderer
        from .bitmask_type_py_renderer import BitmaskTypePyRenderer
        from .function_declaration_py_renderer import FunctionDeclarationPyRenderer

        self.render_table = {
            CallbackInfoType: NullRenderer,
            ObjectType: ObjectTypePyRenderer,
            StructureType: StructureTypePyRenderer,
            EnumType: EnumTypePyRenderer,
            BitmaskType: BitmaskTypePyRenderer,
            FunctionDeclaration: FunctionDeclarationPyRenderer,
        }
