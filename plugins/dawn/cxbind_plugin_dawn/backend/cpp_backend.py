from typing import TYPE_CHECKING
from typing import List

if TYPE_CHECKING:
    from ..program import Program

from pathlib import Path

from loguru import logger
import jinja2
import os

from ..render.cpp.cpp_generator import CppGenerator

from .backend import Backend

class CppBackend(Backend):
    def __init__(self, program: "Program") -> None:
        super().__init__(program)

    def render(self):
        cpp_code = CppGenerator(self).generate()

        # Render the source template
        #source_template = self.jinja_env.get_template("wgpu.cpp.j2")
        source_template = self.jinja_env.get_template("pywgpu.cpp.j2")
        output = source_template.render(cpp_code=cpp_code)
        # logger.debug(output)
        # Write the C++ code to a file
        #path = Path("src/pywgpu.cpp")
        path = Path(self.program.unit.target)
        with open(path, "w") as f:
            f.write(output)

        logger.debug(f"C++ source generated in {path}")

