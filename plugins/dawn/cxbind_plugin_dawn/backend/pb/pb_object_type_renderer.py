from loguru import logger

from ...name import Name
from ...node import Method, RecordMember, StructureType

from ..render_stream import RenderStream
from ..object_type_renderer import ObjectTypeRenderer

from .pb_method_renderer import PbMethodRenderer


class PbObjectTypeRenderer(ObjectTypeRenderer):
    def render(self):
        class_name = self.node.name.CamelCase()

        (
            self.out
            << f'py::class_<{class_name}> _{class_name}(m, "{class_name}");'
            << "\n"
        )
        self.out / f'registry.on(m, "{class_name}", _{class_name});' << "\n\n"
        self.out / f"_{class_name}" << "\n"

        #self.out.indent()
        for method in self.node.methods:
            if self.exclude_method(self.node, method):
                continue

            method_renderer = PbMethodRenderer(self.context, method, self.node)
            method_renderer.render()

        self.out / ";\n"
        #self.out.dedent()
        self.out << "\n"
