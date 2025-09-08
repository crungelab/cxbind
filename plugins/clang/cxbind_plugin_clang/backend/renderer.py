from typing import List, Dict, Tuple, Optional, Union, Any, Callable, Generator
from contextlib import contextmanager

from loguru import logger

from clang import cindex

from .render_context import RenderContext
from ..worker import Worker


class Renderer(Worker[RenderContext]):
    actions: Dict[cindex.CursorKind, Callable] = {}

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
            self.out(self.scope)
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

    @contextmanager
    def enter(self, node) -> Generator[Any, Any, Any]:
        self.session.push_node(node)
        self.out.indent()
        yield node
        self.out.dedent()
        self.session.pop_node()

    def render(self):
        for child in self.node.children:
            renderer = self.context.create_renderer(child)
            renderer.render()
