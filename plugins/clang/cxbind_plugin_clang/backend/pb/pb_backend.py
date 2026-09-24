from ..backend import Backend
from .pb_generator import PbGenerator


class PbBackend(Backend):
    def generate_source(self, result) -> str:
        return PbGenerator(result.source, result.node).generate()

    def default_template(self) -> str:
        return f"{self.unit.name}.cpp"
