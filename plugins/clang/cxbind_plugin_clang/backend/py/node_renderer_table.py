from . import (
    FunctionRenderer,
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
    "ctor": CtorRenderer,
    "field": FieldRenderer,
    "method": MethodRenderer,
    "struct": StructRenderer,
    "class": ClassRenderer,
    "class_template_specialization": ClassTemplateSpecializationRenderer,
    "enum": EnumRenderer,
}
