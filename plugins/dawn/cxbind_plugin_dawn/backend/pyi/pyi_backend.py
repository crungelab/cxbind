from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ...program import Program

from pathlib import Path

from loguru import logger
import jinja2
import os

from .. import Backend

from .pyi_generator import PyiGenerator


class PyiBackend(Backend):
    def __init__(self, program: "Program") -> None:
        super().__init__(program)

    def render(self):
        context = PyiGenerator(self).generate()
        py_code = context.get_text("default")

        # Render the Python bindings
        # Render the source template
        source_template = self.jinja_env.get_template("wgpu_pyi.pyi.j2")
        output = source_template.render(py_code=py_code)
        # logger.debug(output)
        # Write the C++ code to a file
        path = Path(self.program.unit.target)
        with open(path, "w") as f:
            f.write(output)

        logger.debug(f"Python code generated in {path}")
