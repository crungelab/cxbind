import os
from pathlib import Path

from loguru import logger
import jinja2
from rich import print

from cxbind.tool import Tool
from cxbind.unit import Unit
from cxbind.runner.phase import BuildPhase, TransformPhase, GeneratePhase
from cxbind.runner.task import LambdaTask

from cxbind.transform import Transform
from cxbind.transformer import Transformer, _registry as transformer_registry

from .session import Session
from .frontend import Frontend
from .backend.generator import Generator
from .node import Node
from .clang_runner import ClangRunner

class BuildResult:
    def __init__(self, source: str, session: Session, node: Node):
        self.source = source
        self.session = session
        self.node = node

class Compiler(Tool):
    def __init__(self, unit: Unit) -> None:
        super().__init__(unit)

        BASE_PATH = Path(".")
        config_searchpath = BASE_PATH / ".cxbind" / "templates"
        default_searchpath = Path(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)
        self.build_results: list[BuildResult] = []

    def create_transformer(self, transform: Transform) -> Transformer:
        transformer_cls = transformer_registry.get(type(transform))
        if transformer_cls is None:
            logger.warning(
                f"No transformer registered for {type(transform)}. Skipping."
            )
            return None
        return transformer_cls(self.unit)

    def build(self):
        sources = self.unit.sources
        if self.unit.source is not None:
            sources.append(self.unit.source)

        for source in sources:
            self.build_unit(source)

    def build_unit(self, source: str) -> None:
        session = Session(self.unit)
        frontend = Frontend(source, session)
        root = frontend.build()
        runner = ClangRunner.get_current()
        runner.update_specs(session.specs)
        #runner.root.add_child(node)
        for node in root.traverse():
            runner.add_node(node)
        self.build_results.append(BuildResult(source, session, root))

    def generate(self) -> None:
        text_list = []
        for build_result in self.build_results:
            generator = Generator(build_result.source, build_result.session, build_result.node)
            text_list.append(generator.generate())

        text = "\n".join(text_list)

        # Jinja
        context = {"body": text}

        unit_template_path = self.unit.template

        if unit_template_path:
            template = self.jinja_env.get_template(unit_template_path)
        else:
            template = self.jinja_env.get_template(f"{self.unit.name}.cpp")

        rendered = template.render(context)

        filename = self.unit.target
        with open(filename, "w") as fh:
            fh.write(rendered)

        print(f"[bold green]Generated[/bold green]: {filename}", ":thumbs_up:")


    def run(self):
        runner = ClangRunner.get_current()
        plan = runner.plan

        plan.get_phase(BuildPhase).add_task(LambdaTask(self.build))
        plan.get_phase(TransformPhase).add_task(LambdaTask(self.transform))
        plan.get_phase(GeneratePhase).add_task(LambdaTask(self.generate))

    """
    def run(self):
        self.build()

        self.transform()

        self.generate()
    """