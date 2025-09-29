import os
from pathlib import Path
import importlib
from loguru import logger
from rich import print

from clang import cindex

from cxbind.unit import Unit
from .builder import Builder
from .builder_context import BuilderContext

from ..node import Node, RootNode
from ..session import Session

class Frontend(Builder):
    def __init__(self, source: str, session: Session) -> None:
        super().__init__(BuilderContext(session))

        BASE_PATH = Path(".")
        self.path = BASE_PATH / source
        self.mapped.append(self.path.name)
        logger.debug(f"mapped: {self.mapped}")

        self.import_actions()

        self.root = RootNode(kind="root", name="root")
        self.push_node(self.root)
        
    def import_actions(self):
        path = Path(os.path.dirname(os.path.abspath(__file__)), "actions.py")
        spec = importlib.util.spec_from_file_location("actions", path)
        __actions__ = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(__actions__)

        Builder.actions = __actions__.MAP

    def build(self):
        tu = cindex.TranslationUnit.from_source(
            self.path,
            args=self.flags,
            #options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
            options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
        )

        self.visit_overloads(tu.cursor)
        self.visit_children(tu.cursor)

        return self.top_node

    def visit_overloads(self, cursor):
        for child in cursor.get_children():
            if child.kind in [
                cindex.CursorKind.CONSTRUCTOR,
                cindex.CursorKind.CXX_METHOD,
                cindex.CursorKind.FUNCTION_DECL,
            ]:
                key = self.spell(child)
                if key in self.overloaded.visited:
                    self.overloaded.add(key)
                else:
                    self.overloaded.visited.add(key)
            elif self.is_cursor_bindable(child):
                self.visit_overloads(child)
