from .param_builder import ParamBuilder
from .callback_param_builder import CallbackParamBuilder

PARAM_BUILDER_TABLE: dict[str, type[ParamBuilder]] = {
    "callback": CallbackParamBuilder,
}