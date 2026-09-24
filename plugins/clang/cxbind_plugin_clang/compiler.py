import os
from pathlib import Path

from loguru import logger
import jinja2

from cxbind.tool import Tool
from cxbind.unit import Unit
from cxbind.runner.phase import BuildPhase, TransformPhase, GeneratePhase
from cxbind.runner.task import LambdaTask

from cxbind.transform import Transform
from cxbind.transformer import Transformer, _registry as transformer_registry

from .session import Session
from .frontend import Frontend
from .node import Node
from .clang_runner import ClangRunner
from .backend.backend import Backend
from .backend.pb.pb_backend import PbBackend

from .backend.pyi.pyi_backend import PyiBackend

BACKENDS: dict[str, type[Backend]] = {
    "pb": PbBackend,
    "pyi": PyiBackend,
}


class BuildResult:
    def __init__(self, source: str, node: Node):
        self.source = source
        self.node = node


class Compiler(Tool):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)
        self.my_session = Session(self.unit)

        BASE_PATH = Path(".")
        config_searchpath = BASE_PATH / ".cxbind" / "templates"
        default_searchpath = Path(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

        self.build_results: list[BuildResult] = []
        self.backends: list[Backend] = self.create_backends()

    def create_backends(self) -> list[Backend]:
        backends = []
        for kind, target in self.unit.targets.items():
            backend_cls = BACKENDS.get(kind)
            if backend_cls is None:
                raise ValueError(
                    f"{self.unit.name}: clang plugin has no backend for target "
                    f"{kind!r} (supports: {', '.join(BACKENDS)})"
                )
            backends.append(backend_cls(self, target))
        return backends

    def create_transformer(self, transform: Transform) -> Transformer | None:
        transformer_cls = transformer_registry.get(type(transform))
        if transformer_cls is None:
            logger.warning(
                f"No transformer registered for {type(transform)}. Skipping."
            )
            return None
        return transformer_cls(self.unit)

    def build(self):
        # Copy so repeated builds don't keep appending to unit.sources.
        sources = list(self.unit.sources or [])
        if self.unit.source is not None:
            sources.append(self.unit.source)

        for source in sources:
            self.build_source(source)

    def build_source(self, source: str) -> None:
        runner = ClangRunner.get_current()

        session = self.my_session
        session.make_current()

        frontend = Frontend(source)
        root = frontend.build()
        runner.update_specs(session.specs)

        self.build_results.append(BuildResult(source, root))

    def generate(self) -> None:
        if not self.backends:
            logger.warning(f"{self.unit.name}: no targets, nothing to generate")
            return

        session = self.my_session
        session.make_current()

        # All sources and transforms are done: assign final pynames before rendering.
        session.resolve()

        for backend in self.backends:
            backend.run()

    def run(self):
        runner = ClangRunner.get_current()
        plan = runner.plan

        plan.get_phase(BuildPhase).add_task(LambdaTask(self.build))
        plan.get_phase(TransformPhase).add_task(LambdaTask(self.transform))

        if self.unit.generate:
            plan.get_phase(GeneratePhase).add_task(LambdaTask(self.generate))
            for backend in self.backends:
                backend.schedule(runner)
        '''
        if self.unit.generate:
            plan.get_phase(GeneratePhase).add_task(LambdaTask(self.generate))
        '''