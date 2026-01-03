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
    
    def push_stream(self, name: str) -> None:
        stream = self.streams.get(name)
        if stream is None:
            stream = RenderStream()
            self.streams[name] = stream
        self.stream_stack.append(stream)

    def pop_stream(self) -> RenderStream:
        return self.stream_stack.pop()
    
    def init_render_table(self):
        raise NotImplementedError
