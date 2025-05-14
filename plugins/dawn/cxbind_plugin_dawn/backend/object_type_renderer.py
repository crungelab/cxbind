from .renderer import Renderer
from ..node import ObjectType, Method

class ObjectTypeRenderer(Renderer[ObjectType]):
    def exclude_method(self, object_type: ObjectType, method: Method):
        key = f"method/pywgpu::{self.as_cppType(object_type.name)}::{self.as_cppType(method.name)}"
        #print(f"exclude_method: {key}")
        if key in self.context.excluded:
            print(f"method excluded: {key}")
            return True
        return super().exclude_node(method)
