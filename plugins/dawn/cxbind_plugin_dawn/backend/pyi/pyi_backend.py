from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...compiler import Compiler

from pathlib import Path

from loguru import logger
from rich import print

from .. import Backend

from .pyi_generator import PyiGenerator


class PyiBackend(Backend):
    def __init__(self, compiler: "Compiler") -> None:
        super().__init__(compiler)

    def render(self):
        context = PyiGenerator(self).generate()
        py_code = context.get_text("default")

        # Render the Python bindings
        # Render the source template
        source_template = self.jinja_env.get_template("wgpu_pyi.pyi.j2")
        output = source_template.render(py_code=py_code)
        # logger.debug(output)
        # Write the stub code to a file
        path = Path(self.compiler.unit.target)
        with open(path, "w") as f:
            f.write(output)

        #logger.debug(f"Python stub generated in {path}")
        print(f"[bold green]Generated Python stub in[/bold green]: {path}", ":thumbs_up:")
