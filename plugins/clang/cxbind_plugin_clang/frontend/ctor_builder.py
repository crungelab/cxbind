import re

from loguru import logger

from ..node import CtorNode

from .method_builder import MethodBuilder


class CtorBuilder(MethodBuilder):
    def should_cancel(self):
        if self.cursor.is_move_constructor():
            logger.debug(f"Skipping move constructor: {self.cursor.spelling} in {self.top_node.name}")
            return True
        
        if self.cursor.is_copy_constructor():
            logger.debug(f"Skipping copy constructor: {self.cursor.spelling} in {self.top_node.name}")
            return True

        return super().should_cancel()

    def create_node(self):
        name = self.resolve_spelling(self.name)
        self.node = CtorNode(kind='ctor', name=name, cursor=self.cursor)
        #self.node = CtorNode(kind='ctor', name=self.name, cursor=self.cursor)

    def resolve_spelling(self, spelling: str) -> str:
        args = self.context.template_args
        if args:
            replacement = ", ".join(args)
            spelling = re.sub(r'<[^>]*>', f'<{replacement}>', spelling)
        return spelling

    def build_node(self):
        super().build_node()

        if self.top_node.spec.readonly:
            return
                
        self.top_node.has_constructor = True
