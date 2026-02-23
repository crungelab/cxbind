from cxbind.runner import Runner
from cxbind.spec import Spec

from .node import Node, RootNode

class ClangRunner(Runner):
    def __init__(self):
        super().__init__()
        self.root = RootNode(name="root")
        self.specs: dict[str, Spec] = {}

    @classmethod
    def get_current(cls) -> "ClangRunner":
        return Runner.get_current()
    
    def update_specs(self, specs: dict[str, Spec]) -> None:
        self.specs.update(specs)