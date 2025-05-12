from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...backend import Backend

from ..generator import Generator

from .cpp_render_context import CppRenderContext

class CppGenerator(Generator):
    def __init__(self, backend: "Backend") -> None:
        context = CppRenderContext(backend.program.root, backend.jinja_env)
        super().__init__(context, backend)
    
    def render(self):
        self.render_structure_types()
        self.render_object_types()
        self.render_function_declarations()
