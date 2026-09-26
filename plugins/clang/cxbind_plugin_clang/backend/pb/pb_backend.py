from ..backend import Backend
from .pb_generator import PbGenerator


class PbBackend(Backend):
    def generate_source(self, result) -> str:
        return PbGenerator(result.source, result.node).generate()

    def template_name(self) -> str:
        # One .cpp per unit: imgui.cpp.j2
        return f"{self.unit.name}.cpp.j2"

    def fallback_templates(self) -> list[str]:
        return ["default.cpp.j2"]
