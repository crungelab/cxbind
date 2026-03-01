from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator

from loguru import logger

from clang import cindex

from .render_context import RenderContext
from ..worker import Worker


class Renderer(Worker[RenderContext]):
    actions: dict[cindex.CursorKind, Callable] = {}

    def __init__(self, context: RenderContext):
        super().__init__(context)
        self.out = context.out

    @property
    def chaining(self) -> bool:
        return self.context.chaining

    @chaining.setter
    def chaining(self, value) -> None:
        self.context.chaining = value

    def begin_chain(self, emit_scope:bool = True) -> None:
        if self.chaining:
            return
        self.context.chaining = True
        if emit_scope:
            self.out(f"_{self.scope}")
        #self.out(self.scope)

    def end_chain(self) -> None:
        if not self.chaining:
            return
        self.context.chaining = False
        self.out(";")
        self.out()

    @property
    def text(self) -> str:
        return self.out.text

    def render(self):
        pass