from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ..program import Program

from pathlib import Path

from loguru import logger
import jinja2
import os


from .. import Backend

from .hpp_generator import HppGenerator


class HppBackend(Backend):
    def __init__(self, program: "Program") -> None:
        super().__init__(program)

    def render(self):
        hpp_code = HppGenerator(self).generate()

        # Render the header template
        header_template = self.jinja_env.get_template("pywgpu.h.j2")
        output = header_template.render(hpp_code=hpp_code)
        # logger.debug(output)
        # Write the C++ code to a file
        # path = Path("include/dawn/webgpu_cpp.h")
        # path = Path("include/crunge/wgpu/pywgpu.h")
        path = Path(self.program.unit.target)
        with open(path, "w") as f:
            f.write(output)

        logger.debug(f"C++ header generated in {path}")
