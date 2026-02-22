from loguru import logger
from cxbind.unit import Unit

from .transform import Transform
from .transformer import Transformer, _registry as transformer_registry

class Tool():
    def __init__(self, unit: Unit) -> None:
        self.unit = unit

    def run(self):
        pass

    def create_transformer(self, transform: Transform) -> Transformer:
        transformer_cls = transformer_registry.get(type(transform))
        if transformer_cls is None:
            logger.warning(f"No transformer registered for {type(transform)}. Skipping.")
            return None
        return transformer_cls()

    def transform(self):
        transforms = self.unit.transforms
        for transform in transforms:
            transformer = self.create_transformer(transform)
            if transformer is None:
                continue
            transformer.transform(transform)