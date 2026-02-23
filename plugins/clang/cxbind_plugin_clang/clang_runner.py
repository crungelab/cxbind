from cxbind.runner import Runner
from cxbind.spec import Spec

from .node import Node, RootNode

class ClangRunner(Runner):
    def __init__(self):
        super().__init__()
        #self.root = RootNode(name="root")
        self.specs: dict[str, Spec] = {}
        self.nodes: list[Node] = []
        self.nodes_by_name: dict[str, Node] = {}

    @classmethod
    def get_current(cls) -> "ClangRunner":
        return Runner.get_current()
    
    def update_specs(self, specs: dict[str, Spec]) -> None:
        self.specs.update(specs)

    def add_node(self, node: Node):
        self.nodes.append(node)
        self.nodes_by_name[node.name] = node