from ..backend import Backend
from .pb_generator import PbGenerator


class PbBackend(Backend):
    def generate_source(self, result) -> str:
        return PbGenerator(result.source, result.node).generate()

    def fallback_templates(self) -> list[str]:
        return ["default.cpp.j2"]
