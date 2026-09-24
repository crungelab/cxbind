from typing import TYPE_CHECKING

from rich import print

from cxbind.target import Target

if TYPE_CHECKING:
    from ..compiler import Compiler, BuildResult


class Backend:
    """Produces one target from the compiler's resolved build results."""

    def __init__(self, compiler: "Compiler", target: Target) -> None:
        self.compiler = compiler
        self.target = target

    @property
    def unit(self):
        return self.compiler.unit

    def run(self) -> None:
        self.process()
        self.render()

    def process(self) -> None:
        """Hook for backend-local preparation. Nodes are already resolved."""

    def render(self) -> None:
        text = "\n".join(
            self.generate_source(result) for result in self.compiler.build_results
        )

        template_name = self.target.template or self.default_template()
        template = self.compiler.jinja_env.get_template(template_name)
        rendered = template.render({"body": text})

        filename = self.target.path
        with open(filename, "w") as fh:
            fh.write(rendered)

        print(f"[bold green]Generated[/bold green]: {filename}", ":thumbs_up:")

    # --- hooks -----------------------------------------------------------

    def generate_source(self, result: "BuildResult") -> str:
        raise NotImplementedError

    def default_template(self) -> str:
        raise NotImplementedError
