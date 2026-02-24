from cxbind.transform import Transform, register_transform


@register_transform("mogrify")
class Mogrify(Transform):
    target: str