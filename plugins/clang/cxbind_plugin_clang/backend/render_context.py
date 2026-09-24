from typing import TYPE_CHECKING, Optional
from contextvars import ContextVar

from loguru import logger

from cxbind.render_stream import RenderStream

from ..node import Node
from ..work_context import WorkContext

if TYPE_CHECKING:
    from .renderer import Renderer

current_render_context: ContextVar[Optional["RenderContext"]] = ContextVar(
    "current_render_context", default=None
)


class RenderContext(WorkContext):
    """Stream management shared by all backends.

    Subclasses supply `create_renderer`, which decides which renderer
    family (pb, pyi, ...) a node is rendered with.
    """

    def __init__(self) -> None:
        super().__init__()
        self.streams: dict[str, RenderStream] = {}
        self.stream_stack: list[RenderStream] = []
        self.push_stream("default")

    def make_current(self):
        current_render_context.set(self)

    @classmethod
    def get_current(cls) -> Optional["RenderContext"]:
        return current_render_context.get()

    # --- streams ---------------------------------------------------------

    @property
    def out(self) -> RenderStream:
        return self.stream_stack[-1]

    def get_stream(self, name: str) -> RenderStream:
        return self.streams[name]

    def get_text(self, name: str) -> str:
        stream = self.streams.get(name)
        if stream is None:
            return ""
        return stream.text

    def open_stream(self, name: str) -> RenderStream:
        stream = self.streams.get(name)
        if stream is None:
            indentation = self.stream_stack[-1].indentation if self.stream_stack else 0
            stream = RenderStream(indentation)
            self.streams[name] = stream
        return stream

    def close_stream(self, name: str) -> None:
        pass

    def destroy_stream(self, name: str) -> None:
        if name in self.streams:
            del self.streams[name]

    def destroy_streams(self, names: list[str]) -> None:
        for name in names:
            self.destroy_stream(name)

    def push_stream(self, name: str) -> None:
        self.stream_stack.append(self.open_stream(name))

    def pop_stream(self, destroy: bool = False) -> RenderStream:
        stream = self.stream_stack.pop()
        if destroy:
            for key, val in self.streams.items():
                if val is stream:
                    del self.streams[key]
                    break
        return stream

    def combine_streams(self, streams: list[RenderStream]) -> None:
        for stream in streams:
            self.out.inject(stream)

    # --- renderers -------------------------------------------------------

    def create_renderer(self, node: Node) -> "Renderer":
        raise NotImplementedError(
            f"{type(self).__name__} does not implement create_renderer"
        )

    def render_node(self, node: Node) -> None:
        renderer = self.create_renderer(node)
        if renderer is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return
        renderer.render()
