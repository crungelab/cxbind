from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ..backend import Backend

from loguru import logger

from cxbind_plugin_dawn.backend.render_context import RenderContext

from ..node import Node
from .renderer import Renderer

SpecialStructures = ["chained struct", "chained struct out", "INTERNAL_HAVE_EMDAWNWEBGPU_HEADER"]
SpecialFunctions = ["get proc address", "get proc address 2"]
SpecialEnums = ["optional bool"]

class Generator(Renderer):
    def __init__(self, context: RenderContext, backend: "Backend") -> None:
        super().__init__(context)
        self.backend = backend

    def generate(self) -> str:
        self.render()
        return self.context.out.text
    
    def render(self):
        pass

    def exclude_enum_type(self, enum_type):
        if enum_type.name.get() in SpecialEnums:
            return True
        return super().exclude_node(enum_type)

    def exclude_structure_type(self, structure_type):
        if structure_type.name.get() in SpecialStructures:
            return True
        return super().exclude_node(structure_type)

    def exclude_object_type(self, object_type):
        return super().exclude_node(object_type)

    def exclude_function_declaration(self, function_declaration):
        if function_declaration.name.get() in SpecialFunctions:
            return True
        return super().exclude_node(function_declaration)

    def render_bitmask_types(self):
        for bitmask_type in self.backend.bitmask_types:
            #logger.debug(f"Rendering bitmask type: {bitmask_type}")
            self.render_node(bitmask_type)

    def render_enum_types(self):
        for enum_type in self.backend.enum_types:
            if self.exclude_enum_type(enum_type):
                continue
            self.render_node(enum_type)

    def render_structure_types(self):
        for structure_type in self.backend.structure_types:
            if self.exclude_structure_type(structure_type):
                continue
            self.render_node(structure_type)

    def render_object_types(self):
        for object_type in self.backend.object_types:
            self.render_node(object_type)

    def render_function_declarations(self):
        #logger.debug("Rendering function declarations")
        for fn_decl in self.backend.function_declarations:
            if self.exclude_function_declaration(fn_decl):
                continue
            #logger.debug(f"Rendering function declaration: {fn_decl}")
            self.render_node(fn_decl)

    def render_node(self, node: Node):
        renderer_class = self.context.render_table.get(type(node))
        if renderer_class is None:
            raise NotImplementedError(f"Renderer for {type(node)} not implemented")
        renderer = renderer_class(self.context, node)
        renderer.render()