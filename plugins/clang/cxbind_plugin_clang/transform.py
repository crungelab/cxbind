from cxbind.transform import Transform, register_transform


@register_transform("handle")
class HandleTransform(Transform):
    target: str