from ...node import Node

from ..renderer import Renderer

from . import (
    FunctionRenderer,
    FunctionTemplateSpecializationRenderer,
    CtorRenderer,
    FieldRenderer,
    MethodRenderer,
    StructRenderer,
    ClassRenderer,
    ClassTemplateSpecializationRenderer,
    EnumRenderer,
)

NODE_RENDERER_TABLE = {
    "function": FunctionRenderer,
    "function_template_specialization": FunctionTemplateSpecializationRenderer,
    "ctor": CtorRenderer,
    "field": FieldRenderer,
    "method": MethodRenderer,
    "struct": StructRenderer,
    "class": ClassRenderer,
    "class_template_specialization": ClassTemplateSpecializationRenderer,
    "enum": EnumRenderer,
}


class NodeRendererManufacturer:
    @staticmethod
    def create_renderer(node: Node) -> Renderer:
        renderer_cls = NODE_RENDERER_TABLE.get(node.kind)
        if renderer_cls is None:
            raise ValueError(f"Unsupported node kind: {node.kind}")
        return renderer_cls(node)
