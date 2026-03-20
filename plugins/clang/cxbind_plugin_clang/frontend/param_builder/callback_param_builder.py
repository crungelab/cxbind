from loguru import logger

from ...node import Node, CallbackParam

from .param_builder import ParamBuilder


class CallbackParamBuilder(ParamBuilder):
    def create_parameter(self):
        self.param = CallbackParam(
            name=self.info.name,
            type=self.param_type,
        )

    def build_param(self):
        super().build_param()

        logger.debug(f"CallbackParamBuilder: {self.param}")
        for child in self.param.cursor.get_children():
            logger.debug(f"CallbackParamBuilder child kind: {child.kind}")
            child_type = child.type
            logger.debug(f"CallbackParamBuilder child type: {child_type.spelling}")
            logger.debug(f"CallbackParamBuilder child type kind: {child_type.kind}")
            child_decl = child_type.get_declaration()
            logger.debug(f"CallbackParamBuilder child declaration: {child_decl.kind}")
            for parm_cursor in child_decl.get_children():
                logger.debug(f"CallbackParamBuilder child parameter: {parm_cursor.spelling} type: {parm_cursor.type.spelling}")

        key = Node.make_key(child_decl)
        from ..function_prototype_builder import FunctionPrototypeBuilder
        name = child_decl.spelling
        node = self.runner.node_registry.get(key)
        if node is not None:
            logger.debug(f"Found existing node for callback parameter: {node}")
            self.param.function_prototype = node
            return
        builder = FunctionPrototypeBuilder(name, child_decl)
        builder.build()
        function_prototype = builder.node
        logger.debug(f"CallbackParamBuilder function prototype: {function_prototype}")
        self.param.function_prototype = function_prototype

    """
    def build_param(self):
        super().build_param()

        logger.debug(f"CallbackParamBuilder: {self.param}")
        for child in self.param.cursor.get_children():
            logger.debug(f"CallbackParamBuilder child kind: {child.kind}")
            child_type = child.type
            logger.debug(f"CallbackParamBuilder child type: {child_type.spelling}")
            logger.debug(f"CallbackParamBuilder child type kind: {child_type.kind}")
            child_decl = child_type.get_declaration()
            logger.debug(f"CallbackParamBuilder child declaration: {child_decl.kind}")
            for parm_cursor in child_decl.get_children():
                logger.debug(f"CallbackParamBuilder child parameter: {parm_cursor.spelling} type: {parm_cursor.type.spelling}")

        from ..function_prototype_builder import FunctionPrototypeBuilder
        name = child_decl.spelling
        builder = FunctionPrototypeBuilder(name, child_decl)
        builder.build()
        function_prototype = builder.node
        logger.debug(f"CallbackParamBuilder function prototype: {function_prototype}")
        self.param.function_prototype = function_prototype
    """