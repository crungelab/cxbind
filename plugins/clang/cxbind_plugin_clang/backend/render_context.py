from typing import TYPE_CHECKING, Type, Optional
import contextlib
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
    def __init__(self) -> None:
        super().__init__()
        # self.out = RenderStream()
        self.streams: dict[str, RenderStream] = {}
        self.stream_stack: list[RenderStream] = []
        self.push_stream("default")

        self.chaining = False

    def make_current(self):
        current_render_context.set(self)

    @classmethod
    def get_current(cls) -> Optional["RenderContext"]:
        return current_render_context.get()

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
            indentation = 0
            if len(self.stream_stack):
                indentation = self.stream_stack[-1].indentation
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
        stream = self.streams.get(name)
        if stream is None:
            indentation = 0
            if len(self.stream_stack):
                indentation = self.stream_stack[-1].indentation
            stream = RenderStream(indentation)
            self.streams[name] = stream
        self.stream_stack.append(stream)

    def pop_stream(self, destroy: bool = False) -> RenderStream:
        # return self.stream_stack.pop()
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

    def create_renderer(self, node: Node) -> "Renderer":
        from .pb.node_renderer_manufacturer import NodeRendererManufacturer
        return NodeRendererManufacturer.create_renderer(node)

    '''
    def create_renderer(self, node: Node) -> "Renderer":
        from .pb.node_renderer_manufacturer import NODE_RENDERER_TABLE

        cls: Type = NODE_RENDERER_TABLE.get(node.kind, None)
        if cls is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return None
        renderer = cls(node)
        return renderer
    '''

    def render_node(self, node: Node) -> None:
        renderer = self.create_renderer(node)
        if renderer is None:
            logger.warning(f"No renderer for node kind: {node.kind}")
            return
        renderer.render()
