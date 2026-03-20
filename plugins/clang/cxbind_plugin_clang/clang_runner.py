from cxbind.runner import Runner
from cxbind.spec import Spec

from .node import Node
from .node_registry import NodeRegistry


class ClangRunner(Runner):
    def __init__(self):
        super().__init__()
        self.specs: dict[str, Spec] = {}
        #self.nodes: list[Node] = []
        #self.nodes_by_name: dict[str, Node] = {}
        self.node_registry = NodeRegistry()

    @classmethod
    def get_current(cls) -> "ClangRunner | None":
        return super().get_current()

    def register_node(self, node: Node) -> None:
        self.node_registry.register(node)

    """
    @classmethod
    def get_current(cls) -> "ClangRunner":
        return Runner.get_current()
    """

    def update_specs(self, specs: dict[str, Spec]) -> None:
        self.specs.update(specs)
    """
    def add_node(self, node: Node):
        self.nodes.append(node)
        self.nodes_by_name[node.name] = node
    """