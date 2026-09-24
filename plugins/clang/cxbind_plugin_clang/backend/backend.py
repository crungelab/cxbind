from typing import TYPE_CHECKING

import jinja2
from rich import print

from cxbind.target import Target

if TYPE_CHECKING:
    from ..compiler import Compiler, BuildResult
    from cxbind.runner.plan import Plan


class Backend:
    """Produces one target from the compiler's resolved build results."""

    def __init__(self, compiler: "Compiler", target: Target) -> None:
        self.compiler = compiler
        self.target = target

    @property
    def unit(self):
        return self.compiler.unit

    def schedule(self, runner) -> None:
        """Hook: register any extra runner tasks (called from Compiler.run)."""

    def run(self) -> None:
        self.process()
        self.render()

    def process(self) -> None:
        """Hook for backend-local preparation. Nodes are already resolved."""

    def render(self) -> None:
        text = self.render_body()
        template = self.select_template()
        self.write(template.render({"body": text}))

    # --- pieces subclasses can reuse ------------------------------------

    def render_body(self) -> str:
        return "\n".join(
            self.generate_source(result) for result in self.compiler.build_results
        )

    def select_template(self) -> jinja2.Template:
        name = self.target.template or self.default_template()
        return self.compiler.jinja_env.get_or_select_template(name)

    def write(self, rendered: str) -> None:
        filename = self.target.path
        with open(filename, "w") as fh:
            fh.write(rendered)
        print(f"[bold green]Generated[/bold green]: {filename}", ":thumbs_up:")

    # --- hooks -----------------------------------------------------------

    def generate_source(self, result: "BuildResult") -> str:
        raise NotImplementedError

    def default_template(self) -> str | list[str]:
        raise NotImplementedError
