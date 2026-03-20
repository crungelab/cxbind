from loguru import logger

from cxbind.facade import CallbackFacade

from ....node import Parameter, CallbackParam

from .param_renderer import FacadeParamRenderer


class CallbackParamRenderer(FacadeParamRenderer[CallbackFacade]):
    param: CallbackParam
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.context_param = self.facade.context_param

    def excludes(self) -> set[str]:
        return {self.context_param}

    def render_param(self, private=False):
        out = self.out
        out << f"py::function " << self.param.name

    def render_arg(self, private=False) -> None:
        super().render_arg(private=True)

    def render(self):
        logger.debug(f"CallbackParamRenderer: {self.param.name} type: {self.param.type.spelling}")
        logger.debug(f"CallbackParamRenderer function prototype: {self.param.function_prototype}")

        out = self.out
        param_name = self.param.name
        param_type = self.param.type

        thunk_params = self.param.function_prototype.params
        thunk_param_string = ", ".join([f"{p.type.spelling} {p.name}" for p in thunk_params])
        thunk_args_string = ", ".join([p.name for p in thunk_params if p.name != self.context_param])
        thunk_return_value = self.param.function_prototype.returns
        thunk_return_string = thunk_return_value.type.spelling if thunk_return_value is not None else "void"
        value = f"""\
        cxbind::thunk_state _{self.context_param}({param_name});
        auto {self.context_param} = &_{self.context_param};
        auto _{param_name} = +[]({thunk_param_string}) -> bool {{
            auto& ts = *static_cast<cxbind::thunk_state*>({self.context_param});
            // ... use ts, acquire GIL, call Python, etc ...
            py::gil_scoped_acquire gil;
            py::object result = ts.cb({thunk_args_string});
            return result.cast<{thunk_return_string}>();
        }};
        """
        out(value)

    '''
    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        value = f"""\
        cxbind::thunk_state _{self.context_param}({param_name});
        auto {self.context_param} = &_{self.context_param};
        auto _{param_name} = +[](int value, void* ctx) -> bool {{
            auto& ts = *static_cast<cxbind::thunk_state*>(ctx);
            // ... use ts, acquire GIL, call Python, etc ...
            py::gil_scoped_acquire gil;
            py::object result = ts.cb(value);
            return result.cast<bool>();
        }};
        """
        out(value)

        logger.debug(f"CallbackParamRenderer: {self.param.name} type: {self.param.type.spelling}")
        logger.debug(f"CallbackParamRenderer function prototype: {self.param.function_prototype}")
    '''