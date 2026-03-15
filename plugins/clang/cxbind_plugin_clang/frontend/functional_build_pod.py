from clang import cindex

from ..node import FunctionalNode, Argument

from .build_pod import BuildPod

from .arg_builder import ArgBuilder

class FunctionalBuildPod(BuildPod):
    node: FunctionalNode
    def __init__(self, node: FunctionalNode):
        super().__init__(node)
