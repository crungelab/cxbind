import os
from pathlib import Path

from loguru import logger
import jinja2

from clang import cindex

from cxbind.unit import Unit

from ..node import RootNode
from ..session import Session

from .render_context import RenderContext
from .renderer import Renderer
from .py import NodeRenderer


class Generator(NodeRenderer):
    def __init__(self, source: str, session: Session, node: RootNode, **kwargs):
        super().__init__(RenderContext(session, **kwargs), node)

        BASE_PATH = Path(".")
        self.path = BASE_PATH / source

        config_searchpath = BASE_PATH / ".cxbind" / "templates"
        default_searchpath = Path(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

    def generate(self):
        with self.out:
            self.render()
            self.end_chain()

        return self.text
