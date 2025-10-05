from loguru import logger
from .method_builder import MethodBuilder
from ..node import CtorNode


class CtorBuilder(MethodBuilder):
    def should_cancel(self):
        '''
        if self.top_node is None:
            return True
        '''
        if self.cursor.is_move_constructor():
            logger.debug(f"Skipping move constructor: {self.cursor.spelling} in {self.top_node.name}")
            return True
        
        if self.cursor.is_copy_constructor():
            logger.debug(f"Skipping copy constructor: {self.cursor.spelling} in {self.top_node.name}")
            return True

        return super().should_cancel()

    def create_node(self):
        self.node = CtorNode(kind='ctor', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()
        #NodeBuilder.build_node(self)

        if self.top_node.spec.readonly:
            return
                
        self.top_node.has_constructor = True
