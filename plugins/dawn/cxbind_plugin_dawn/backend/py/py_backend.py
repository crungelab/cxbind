from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ...compiler import Compiler

from pathlib import Path

from loguru import logger
import jinja2
import os

from .. import Backend

from .py_generator import PyGenerator


class PyBackend(Backend):
    def __init__(self, compiler: "Compiler") -> None:
        super().__init__(compiler)

    def render(self):
        context = PyGenerator(self).generate()
        py_code = context.get_text("default")

        # Render the Python bindings
        # Render the source template
        source_template = self.jinja_env.get_template("wgpu_py.py.j2")
        output = source_template.render(py_code=py_code)
        # logger.debug(output)
        # Write the C++ code to a file
        path = Path(self.compiler.unit.target)
        with open(path, "w") as f:
            f.write(output)

        logger.debug(f"Python code generated in {path}")
