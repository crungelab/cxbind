from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ...compiler import Compiler

from pathlib import Path

from loguru import logger
import jinja2
import os


from .. import Backend

from .hpp_generator import HppGenerator


class HppBackend(Backend):
    def __init__(self, compiler: "Compiler") -> None:
        super().__init__(compiler)

    def render(self):
        context = HppGenerator(self).generate()
        hpp_code = context.get_text("default")

        # Render the header template
        header_template = self.jinja_env.get_template("pywgpu.h.j2")
        output = header_template.render(hpp_code=hpp_code)
        # logger.debug(output)
        # Write the C++ code to a file
        path = Path(self.compiler.unit.target)
        with open(path, "w") as f:
            f.write(output)

        logger.debug(f"C++ header generated in {path}")
