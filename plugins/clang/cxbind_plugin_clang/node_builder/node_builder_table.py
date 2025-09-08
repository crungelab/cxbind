from . import (
    FunctionBuilder,
    CtorBuilder,
    FieldBuilder,
    MethodBuilder,
    StructBuilder,
    ClassBuilder,
    ClassTemplateBuilder,
    EnumBuilder,
)

NODE_BUILDER_TABLE = {
    "function": FunctionBuilder,
    "ctor": CtorBuilder,
    "field": FieldBuilder,
    "method": MethodBuilder,
    "struct": StructBuilder,
    "class": ClassBuilder,
    "class_template": ClassTemplateBuilder,
    "enum": EnumBuilder,
}
