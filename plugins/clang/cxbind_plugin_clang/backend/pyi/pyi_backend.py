from collections import Counter

from loguru import logger

from ..backend import Backend
from .pyi_generator import PyiGenerator
from .stub_assembler import StubAssembler, StubFragment, Import


class PyiBackend(Backend):
    assembler: StubAssembler

    def schedule(self, runner) -> None:
        self.assembler = StubAssembler.for_runner(runner)

    def process(self) -> None:
        self.missing: Counter[tuple[str, str | None]] = Counter()
        self.unmapped: Counter[str] = Counter()
        self.imports: set[Import] = set()

    def generate_source(self, result) -> str:
        generator = PyiGenerator(result.source, result.node)
        text = generator.generate()
        self.missing.update(generator.context.missing)
        self.unmapped.update(generator.context.types.unmapped)
        self.imports |= generator.context.imports
        return text

    def default_template(self) -> list[str]:
        # Per-unit template if one exists, otherwise the generic stub template.
        return [f"{self.unit.name}.pyi", "default.pyi"]

    def render(self) -> None:
        # Don't write: several units may share this stub. The assembler
        # writes each path once, in AssemblyPhase.
        fragment = StubFragment(
            unit=self.unit.name,
            module=self.unit.module,
            body=self.render_body(),
            template=self.select_template(),
            imports=self.imports,
        )
        self.assembler.add(self.target.path, fragment)
        self.report()

    def report(self) -> None:
        name = self.unit.name
        if self.missing:
            lines = "\n".join(
                f"  {count:5d}  kind={kind}, facade={facade}"
                for (kind, facade), count in self.missing.most_common()
            )
            logger.warning(f"{name}: no pyi renderer for:\n{lines}")
        if self.unmapped:
            lines = "\n".join(
                f"  {count:5d}  {spelling}"
                for spelling, count in self.unmapped.most_common()
            )
            logger.warning(f"{name}: typed as Any:\n{lines}")
