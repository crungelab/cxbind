import jinja2

from .render_stream import RenderStream
from ..node import Root, Catalog

class RenderContext:
    def __init__(self, root: Root, jinja_env: jinja2.Environment) -> None:
        self.root = root
        self.catalog = Catalog()
        for key, value in self.root.root.items():
            self.catalog.add_entry(value)
        self.jinja_env = jinja_env
        self.out = RenderStream()
        self.render_table = {}
        self.init_render_table()
        #
        self.c_prefix = "WGPU"

    def init_render_table(self):
        raise NotImplementedError
