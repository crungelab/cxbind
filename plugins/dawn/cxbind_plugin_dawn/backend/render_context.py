from typing import List, Dict

import jinja2

from cxbind.unit import Unit

from .render_stream import RenderStream
from ..node import Root, Catalog

class RenderContext:
    def __init__(self, unit: Unit, root: Root, jinja_env: jinja2.Environment) -> None:
        self.unit = unit
        self.excludes = unit.excludes.copy()
        self.excluded = set(self.excludes)
        
        self.root = root
        self.catalog = Catalog()
        for key, value in self.root.root.items():
            self.catalog.add_entry(value)
        self.jinja_env = jinja_env

        #self.out = RenderStream()
        self.streams: Dict[str, RenderStream] = {}
        self.stream_stack: List[RenderStream] = []
        self.push_stream("default")

        self.render_table = {}
        self.init_render_table()
        #
        self.c_prefix = "WGPU"

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

    def destroy_streams(self, names: List[str]) -> None:
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
        #return self.stream_stack.pop()
        stream = self.stream_stack.pop()
        if destroy:
            for key, val in self.streams.items():
                if val is stream:
                    del self.streams[key]
                    break
        return stream
    
    def combine_streams(self, streams: List[RenderStream]) -> None:
        for stream in streams:
            self.out.inject(stream)
    
    def init_render_table(self):
        raise NotImplementedError
