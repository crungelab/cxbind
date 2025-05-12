from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ...backend import Backend

from ..generator import Generator

from .py_render_context import PyRenderContext

SpecialStructures = ["string view", "nullable string view"]

class PyGenerator(Generator):
    def __init__(self, backend: "Backend") -> None:
        context = PyRenderContext(backend.program.root, backend.jinja_env)
        super().__init__(context, backend)

    def exclude_structure_type(self, structure_type):
        if structure_type.name.get() in SpecialStructures:
            return True
        return super().exclude_structure_type(structure_type)
    
    def render(self):
        self.render_enum_types()
        self.render_bitmask_types()
        self.render_object_types()
        self.render_structure_types()
        self.render_function_declarations()
