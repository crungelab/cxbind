from dataclasses import dataclass

from clang import cindex

from cxbind.facade import Facade

from ..node import FunctionalNode

from .build_pod import BuildPod


@dataclass(slots=True)
class ParamInfo:
    name: str
    type: cindex.Type
    cursor: cindex.Cursor | None = None
    facade: Facade | None = None


class FunctionalBuildPod(BuildPod):
    node: FunctionalNode

    def __init__(self, node: FunctionalNode):
        super().__init__(node)
