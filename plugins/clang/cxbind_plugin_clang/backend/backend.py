from typing import TYPE_CHECKING, Any
from pathlib import Path

import jinja2
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

    def schedule(self, runner) -> None:
        """Hook: register any extra runner tasks (called from Compiler.run)."""

    def run(self) -> None:
        self.process()
        self.render()

    def process(self) -> None:
        """Hook for backend-local preparation. Nodes are already resolved."""

    def render(self) -> None:
        template = self.select_template()
        self.write(template.render(self.template_context(self.render_body())))

    # --- pieces subclasses can reuse ------------------------------------

    def render_body(self) -> str:
        return "\n".join(
            self.generate_source(result) for result in self.compiler.build_results
        )

    def template_context(self, body: str) -> dict[str, Any]:
        return {
            "body": body,
            "unit": self.unit,
            "target": self.target,
            "sources": [result.source for result in self.compiler.build_results],
        }

    def select_template(self) -> jinja2.Template:
        name = self.target.template or self.default_template()
        return self.compiler.jinja_env.get_or_select_template(name)

    def default_template(self) -> list[str]:
        # Named after the file it produces: src/foo_py_auto.cpp -> foo_py_auto.cpp.j2
        return [f"{Path(self.target.path).name}.j2", *self.fallback_templates()]

    def fallback_templates(self) -> list[str]:
        """Generic templates to try when the target has none of its own."""
        return []

    def write(self, rendered: str) -> None:
        if not rendered.endswith("\n"):
            rendered += "\n"
        path = Path(self.target.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            fh.write(rendered)
        print(f"[bold green]Generated[/bold green]: {path}", ":thumbs_up:")

    # --- hooks -----------------------------------------------------------

    def generate_source(self, result: "BuildResult") -> str:
        raise NotImplementedError
