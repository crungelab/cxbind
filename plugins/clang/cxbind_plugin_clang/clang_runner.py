import sys
from loguru import logger
from clang import cindex
import os

from cxbind.runner import Runner
from cxbind.spec import Spec

from .node import Node
from .node_registry import NodeRegistry


class ClangRunner(Runner):
    def __init__(self, project):
        super().__init__(project)
        self.specs: dict[str, Spec] = {}
        self.node_registry = NodeRegistry()

        _configure_libclang()

    @classmethod
    def get_current(cls) -> "ClangRunner | None":
        return super().get_current()

    def register_node(self, node: Node) -> None:
        self.node_registry.register(node)

    def update_specs(self, specs: dict[str, Spec]) -> None:
        self.specs.update(specs)

_libclang_configured = False

def _configure_libclang():
    global _libclang_configured
    if _libclang_configured:
        return
    if sys.platform == "darwin":
        cindex.Config.set_library_path("/usr/local/opt/llvm@6/lib")
    elif sys.platform == "linux":
        cindex.Config.set_library_file(
            os.environ.get("CXBIND_LIBCLANG", "/usr/lib/llvm-21/lib/libclang-21.so.1")
        )
    else:
        cindex.Config.set_library_path("C:/Program Files/LLVM/bin")
    _libclang_configured = True