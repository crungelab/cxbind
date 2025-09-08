import os
from pathlib import Path

from loguru import logger
import jinja2

from clang import cindex

from cxbind.unit import Unit

from .render_context import RenderContext
from .renderer import Renderer
from .py import NodeRenderer


class Generator(Renderer):
    def __init__(self, source: str, unit: Unit, **kwargs):
        super().__init__(RenderContext(unit, **kwargs))

        BASE_PATH = Path(".")
        self.path = BASE_PATH / source

        config_searchpath = BASE_PATH / ".cxbind" / "templates"
        default_searchpath = Path(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )
        searchpath = [config_searchpath, default_searchpath]
        loader = jinja2.FileSystemLoader(searchpath=searchpath)
        self.jinja_env = jinja2.Environment(loader=loader)

    def generate(self, root):
        tu = cindex.TranslationUnit.from_source(
            self.path,
            args=self.flags,
            options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
        )

        with self.out:
            renderer = NodeRenderer(self.context, root)
            renderer.render()
            self.end_chain()

        return self.out.text

    '''
    def generate(self, nodes):
        tu = cindex.TranslationUnit.from_source(
            self.path,
            args=self.flags,
            options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
        )

        with self.out:
            for node in nodes:
                logger.debug(f"Rendering Node: {node})")
                renderer = self.context.create_renderer(node)
                renderer.render()
            self.end_chain()

        return self.out.text
    '''