from loguru import logger

from cxbind.unit import Unit
from cxbind.extra import ExtraStandardMethod
from .transform import Mogrify
from .node import Node, FunctionNode
from .clang_runner import ClangRunner

class MogrifyTransformer:
    def __init__(self, unit: Unit):
        self.unit = unit

    def transform(self, transform: Mogrify):
        runner = ClangRunner.get_current()
        logger.debug(f"Transforming spec: {transform.target}")

        spec = self.unit.specs.get(transform.target)

        if spec is None:
            raise ValueError(f"Spec not found for target: {transform.target}")
        logger.debug(f"Spec: {spec}")

        spec_name = spec.name

        spec_node = runner.nodes_by_name.get(spec_name)
        if spec_node is None:
            raise ValueError(f"Node not found for spec: {spec_name}")
        logger.debug(f"Spec node: {spec_node}")

        target_pyname = spec.pyname or spec_node.pyname

        #root = runner.root
        #logger.debug(f"Root node: {root}")

        #for node in root.traverse():
        for node in runner.nodes:
            logger.debug(f"Checking node: {node}")
            if not isinstance(node, FunctionNode):
                continue
            logger.debug(f"Checking function node: {node.name}")
            first_arg = node.args[0] if node.args else None
            logger.debug(f"First argument: {first_arg}")
            #if first_arg and first_arg.type == name:
            if first_arg and spec_name in first_arg.type:
                logger.debug(f"Found matching function node: {node}")
                #spec.extra.add_method(ExtraStandardMethod(name=node.name, use=node.name))
                name = node.pyname
                name = name.removeprefix(target_pyname.lower() + "_")
                name = name.removesuffix("_" + target_pyname.lower())
                spec.extra.add_method(ExtraStandardMethod(name=name, use=node.name))
