from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...compiler import Compiler

from pathlib import Path

from loguru import logger
from rich import print

from .. import Backend

from .cpp_generator import CppGenerator


class CppBackend(Backend):
    def __init__(self, compiler: "Compiler") -> None:
        super().__init__(compiler)

    def render(self):
        context = CppGenerator(self).generate()
        cpp_code = context.get_text("default")

        # Render the source template
        # source_template = self.jinja_env.get_template("wgpu.cpp.j2")
        source_template = self.jinja_env.get_template("pywgpu.cpp.j2")
        output = source_template.render(cpp_code=cpp_code)
        # logger.debug(output)
        # Write the C++ code to a file
        path = Path(self.compiler.unit.target)
        with open(path, "w") as f:
            f.write(output)

        #logger.debug(f"C++ source generated in {path}")
        print(f"[bold green]Generated C++ source in[/bold green]: {path}", ":thumbs_up:")
