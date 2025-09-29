from . import (
    FunctionBuilder,
    FunctionTemplateBuilder,
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
    "function_template": FunctionTemplateBuilder,
    "ctor": CtorBuilder,
    "field": FieldBuilder,
    "method": MethodBuilder,
    "struct": StructBuilder,
    "class": ClassBuilder,
    "class_template": ClassTemplateBuilder,
    "enum": EnumBuilder,
}
