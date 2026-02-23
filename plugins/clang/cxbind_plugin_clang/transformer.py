from loguru import logger

from cxbind.unit import Unit

from .transform import HandleTransform
from .node import Node, FunctionNode
from .clang_runner import ClangRunner

class HandleTransformer:
    def __init__(self, unit: Unit):
        self.unit = unit

    def transform(self, transform: HandleTransform):
        runner = ClangRunner.get_current()
        logger.debug(f"Transforming spec: {transform.target}")
        spec = self.unit.specs[transform.target]
        logger.debug(f"Spec: {spec}")
        name = spec.name
        root = runner.root
        logger.debug(f"Root node: {root}")

        for node in root.traverse():
            logger.debug(f"Checking node: {node}")
            if not isinstance(node, FunctionNode):
                continue
            logger.debug(f"Checking function node: {node.name}")
