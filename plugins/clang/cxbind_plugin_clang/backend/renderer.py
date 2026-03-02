from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator

from loguru import logger

from clang import cindex

from .render_context import RenderContext
from ..worker import Worker


class Renderer(Worker[RenderContext]):
    actions: dict[cindex.CursorKind, Callable] = {}

    def __init__(self):
        super().__init__()

    @property
    def current_context(self):
        return RenderContext.get_current()

    @property
    def out(self):
        return self.current_context.out

    @property
    def chaining(self) -> bool:
        return self.current_context.chaining

    @chaining.setter
    def chaining(self, value) -> None:
        self.current_context.chaining = value

    def begin_chain(self, emit_scope:bool = True) -> None:
        if self.chaining:
            return
        self.current_context.chaining = True
        if emit_scope:
            self.out(f"_{self.scope}")
        #self.out(self.scope)

    def end_chain(self) -> None:
        if not self.chaining:
            return
        self.current_context.chaining = False
        self.out(";")
        self.out()

    @property
    def text(self) -> str:
        return self.out.text

    def render(self):
        pass