from .renderer import Renderer
from ..node import ObjectType, Method

class ObjectTypeRenderer(Renderer[ObjectType]):
    def exclude_method(self, method: Method):
        return super().exclude_node(method)
