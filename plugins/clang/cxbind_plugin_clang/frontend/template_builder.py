from typing import TypeVar, Generic

from .node_builder import NodeBuilder
from ..node import TemplateNode

T_Node = TypeVar("T_Node", bound=TemplateNode)


class TemplateBuilder(NodeBuilder[T_Node]):
    pass