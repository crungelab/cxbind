from loguru import logger

from cxbind.unit import Unit

from .transform import HandleTransform
from .node import Node, FunctionNode

class HandleTransformer:
    def __init__(self, unit: Unit, root: Node):
        self.unit = unit
        self.root = root

    def transform(self, transform: HandleTransform):
        logger.debug(f"Transforming spec: {transform.target}")
        spec = self.unit.specs[transform.target]
        logger.debug(f"Spec: {spec}")
        name = spec.name
        logger.debug(f"Root node: {self.root}")

        for node in self.root.traverse():
            logger.debug(f"Checking node: {node}")
            if not isinstance(node, FunctionNode):
                continue
            logger.debug(f"Checking function node: {node.name}")

    """
    def transform(self, transform: HandleTransform):
        logger.debug(f"Transforming spec: {transform.target}")
        spec = self.unit.specs[transform.target]
        logger.debug(f"Spec: {spec}")
        name = spec.name

        for node in self.root.traverse():
            logger.debug(f"Checking node: {node}")
            if node.name == name:
                logger.debug(f"Found target node: {node}")
    """