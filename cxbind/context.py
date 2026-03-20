from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import ClassVar, Generic, Iterator, TypeVar


T = TypeVar("T", bound="Context")


class Context(Generic[T]):
    _current_var: ClassVar[ContextVar[T]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._current_var = ContextVar(f"{cls.__module__}.{cls.__qualname__}.current")

    def make_current(self: T) -> Token[T]:
        return type(self)._current_var.set(self)

    @contextmanager
    def use(self: T) -> Iterator[T]:
        token = self.make_current()
        try:
            yield self
        finally:
            type(self)._current_var.reset(token)

    @classmethod
    def get_current(cls) -> T | None:
        return cls._current_var.get(None)

    @classmethod
    def require_current(cls) -> T:
        current = cls._current_var.get(None)
        if current is None:
            raise RuntimeError(f"No current {cls.__name__} is set")
        return current