from cxbind.spec import SpecKey
from cxbind.transform import Transform, register_transform


@register_transform("mogrify")
class Mogrify(Transform):
    #target: str
    target: SpecKey