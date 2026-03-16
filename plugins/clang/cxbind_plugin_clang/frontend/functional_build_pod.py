from clang import cindex

from ..node import FunctionalNode, Parameter

from .build_pod import BuildPod

from .param_builder import ParamBuilder

class FunctionalBuildPod(BuildPod):
    node: FunctionalNode
    def __init__(self, node: FunctionalNode):
        super().__init__(node)
