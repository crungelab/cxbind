from loguru import logger

from .functional_builder import FunctionalBuilder, ParamInfo
from ..node import FunctionPrototypeNode


class FunctionPrototypeBuilder(FunctionalBuilder[FunctionPrototypeNode]):
    def create_node(self):
        self.node = FunctionPrototypeNode(kind='function_prototype', name=self.name, cursor=self.cursor)

    def build_node(self):
        super().build_node()
        return True # Don't add this node to parent
    
    def get_param_infos(self) -> list[ParamInfo]:
        cursor = self.cursor

        infos = []
        for i, arg_cursor in enumerate(cursor.get_children()):
            name = self.make_arg_name(arg_cursor) or f"arg{i}"
            facade = self.get_param_facade(name, arg_cursor.type)
            infos.append(
                ParamInfo(name=name, type=arg_cursor.type, cursor=arg_cursor, facade=facade)
            )
        return infos
