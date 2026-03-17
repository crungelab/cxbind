from .param_renderer import ParamRenderer
from .pycapsule_param_renderer import PyCapsuleParamRenderer
from .object_param_renderer import ObjectParamRenderer
from .wrapper_param_renderer import WrapperParamRenderer
from .vector_param_renderer import VectorParamRenderer
from .callback_param_renderer import CallbackParamRenderer
from .buffer_param_renderer import BufferParamRenderer


PARAM_RENDERER_TABLE: dict[str, type[ParamRenderer]] = {
    "pycapsule": PyCapsuleParamRenderer,
    "wrapper": WrapperParamRenderer,
    "object": ObjectParamRenderer,
    "vector": VectorParamRenderer,
    "callback": CallbackParamRenderer,
    "buffer": BufferParamRenderer,
}
