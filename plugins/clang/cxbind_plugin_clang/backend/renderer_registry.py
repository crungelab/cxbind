from loguru import logger

from .renderer import Renderer


class RendererRegistry:
    _registry: dict[tuple[str, str | None], type[Renderer]] = {}

    @classmethod
    def register(cls, kind: str, facade: str | None = None):
        def decorator(renderer_cls):
            cls._registry[(kind, facade)] = renderer_cls
            logger.debug(f"Registered renderer: {renderer_cls} for kind={kind}, facade={facade}")
            return renderer_cls

        return decorator

    @classmethod
    def resolve(cls, kind: str, facade: str | None):
        renderer_cls = cls._registry.get((kind, facade))
        return renderer_cls

    """
    @classmethod
    def resolve(cls, kind: str, facade: str | None):
        logger.debug(f"Resolving renderer for kind={kind}, facade={facade}")
        renderer_cls = cls._registry.get((kind, facade))
        if renderer_cls:
            logger.debug(f"Found renderer: {renderer_cls} for kind={kind}, facade={facade}")
        else:
            logger.debug(f"No renderer found for kind={kind}, facade={facade}")
        return renderer_cls
    """