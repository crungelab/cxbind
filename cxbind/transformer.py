from .transform import Transform

_registry: dict[type[Transform], type["Transformer"]] = {}

class Transformer:
    def __init__(self):
        pass

    def transform(self, transform: Transform):
        pass