from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...compiler import Compiler

from pathlib import Path

from loguru import logger
from rich import print

from .. import Backend

from .pb_generator import PbGenerator


class PbBackend(Backend):
    def __init__(self, compiler: "Compiler") -> None:
        super().__init__(compiler)

    def render(self):
        context = PbGenerator(self).generate()
        prologue = context.get_text("prologue")
        py_code = context.get_text("default")
        epilogue = context.get_text("epilogue")

        # Render the Python bindings
        # Render the source template
        source_template = self.jinja_env.get_template("wgpu_pb.cpp.j2")
        output = source_template.render(
            prologue=prologue, py_code=py_code, epilogue=epilogue
        )
        # logger.debug(output)
        # Write the C++ code to a file
        path = Path(self.compiler.unit.target)
        with open(path, "w") as f:
            f.write(output)

        # logger.debug(f"C++ bindings generated in {path}")
        print(
            f"[bold green]Generated C++ bindings in[/bold green]: {path}", ":thumbs_up:"
        )
