from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from .. import Backend

from ..generator import Generator

from .pb_render_context import PbRenderContext

SpecialStructures = ["string view", "nullable string view"]

class PbGenerator(Generator):
    def __init__(self, backend: "Backend") -> None:
        context = PbRenderContext(backend.compiler.unit, backend.compiler.root, backend.jinja_env)
        super().__init__(context, backend)

    def exclude_structure_type(self, structure_type):
        if structure_type.name.get() in SpecialStructures:
            return True
        return super().exclude_structure_type(structure_type)
    
    def render(self):
        self.render_enum_types()
        self.render_bitmask_types()
        self.render_callback_info_types()
        self.render_structure_types()
        self.render_object_types()
        #self.render_structure_types()
        self.render_function_declarations()
        self.render_epilogue()

    def render_epilogue(self):
        self.context.push_stream("epilogue")

        self.out / "ChainedStruct* build_chained_struct(py::handle h, BuildCtx ctx) {" << "\n"
        self.out.indent()
        self.out / "if (h.is_none()) return nullptr;" << "\n"
        self.out / f'auto s_type = py::cast<SType>(h.attr("s_type"));' << "\n"

        self.out / "switch (s_type) {" << "\n"
        self.out.indent()
        for structure_type in self.backend.structure_types:
            if self.exclude_structure_type(structure_type):
                continue
            if not structure_type.chained == "in":
                continue
            self.out / f"case SType::{structure_type.name.CamelCase()}:" << "\n"
            self.out.indent()
            self.out / f"return Builder<{structure_type.name.CamelCase()}>(ctx).build(h);" << "\n"
            self.out.dedent()
        self.out.dedent()
        self.out / "}" << "\n"
        self.out / "return nullptr;" << "\n"
        self.out.dedent()
        self.out / "}" << "\n"