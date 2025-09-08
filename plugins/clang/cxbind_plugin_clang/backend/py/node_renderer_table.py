from . import (
    FunctionRenderer,
    CtorRenderer,
    FieldRenderer,
    MethodRenderer,
    StructRenderer,
    ClassRenderer,
    ClassSpecializationRenderer,
    EnumRenderer,
)

NODE_RENDERER_TABLE = {
    "function": FunctionRenderer,
    "ctor": CtorRenderer,
    "field": FieldRenderer,
    "method": MethodRenderer,
    "struct": StructRenderer,
    "class": ClassRenderer,
    "class_specialization": ClassSpecializationRenderer,
    "enum": EnumRenderer,
}
