from loguru import logger

from ...name import Name
from ...node import FunctionDeclaration, RecordMember, StructureType, ObjectType

from ..render_stream import RenderStream
from ..renderer import Renderer, T_Node

from .pb_render_context import PbRenderContext
from .pb_functional_renderer import PbFunctionalRenderer


class PbFunctionRenderer(PbFunctionalRenderer[FunctionDeclaration]):
    def __init__(self, context: PbRenderContext, node: FunctionDeclaration):
        super().__init__(context, node)
