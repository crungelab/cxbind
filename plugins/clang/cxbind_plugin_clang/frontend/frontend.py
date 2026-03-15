import os
from pathlib import Path
import importlib
from loguru import logger

from clang import cindex

from .builder import Builder
from .build_context import BuildContext

from ..node import RootNode


class Frontend(Builder):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.builder_context = BuildContext()

        BASE_PATH = Path(".")
        self.path = BASE_PATH / source

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
        self.builder_context.make_current()

        self.mapped.add(self.path.name)
        logger.debug(f"mapped: {self.mapped}")

        tu = cindex.TranslationUnit.from_source(
            self.path,
            args=self.flags,
            # options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
            options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
        )

        for diag in tu.diagnostics:
            logger.warning(f"Diagnostic: {diag}")

        self.visit_overloads(tu.cursor)
        logger.debug(f"Overloads: {self.overloaded}")

        self.visit(tu.cursor)

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
                    logger.debug(f"Overloaded function detected: {key}")
                else:
                    self.overloaded.visited.add(key)
            elif self.is_cursor_bindable(child):
                self.visit_overloads(child)
