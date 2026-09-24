from typing import Callable, ClassVar, Generic, TypeVar

from loguru import logger

from .renderer import Renderer

T_Renderer = TypeVar("T_Renderer", bound=type[Renderer])

RegistryKey = tuple[str, str | None]


class RendererRegistry:
    _registry: ClassVar[dict[RegistryKey, type[Renderer]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Each subclass gets its own table so pb and pyi renderers never collide.
        cls._registry = {}

    @classmethod
    def register(
        cls, kind: str, facade: str | None = None
    ) -> Callable[[T_Renderer], T_Renderer]:
        def decorator(renderer_cls: T_Renderer) -> T_Renderer:
            key = (kind, facade)
            if key in cls._registry:
                logger.warning(
                    f"{cls.__name__}: replacing {cls._registry[key]} with {renderer_cls} "
                    f"for kind={kind}, facade={facade}"
                )
            cls._registry[key] = renderer_cls
            logger.debug(
                f"{cls.__name__}: registered {renderer_cls} for kind={kind}, facade={facade}"
            )
            return renderer_cls

        return decorator

    @classmethod
    def resolve(cls, kind: str, facade: str | None) -> type[Renderer] | None:
        return cls._registry.get((kind, facade))


class PbRendererRegistry(RendererRegistry):
    pass


class PyiRendererRegistry(RendererRegistry):
    pass