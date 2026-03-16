from dataclasses import dataclass

from clang import cindex

#from ..node import FunctionalNode, Parameter
from ..node import FunctionalNode

from .build_pod import BuildPod

#from .param_builder import ParamBuilder


@dataclass(slots=True)
class ParamInfo:
    name: str
    type: cindex.Type
    cursor: cindex.Cursor | None = None


class FunctionalBuildPod(BuildPod):
    node: FunctionalNode

    def __init__(self, node: FunctionalNode):
        super().__init__(node)
