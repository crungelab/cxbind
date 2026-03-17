from cxbind.facade import ObjectFacade

from .param_renderer import FacadeParamRenderer

class ObjectParamRenderer(FacadeParamRenderer[ObjectFacade]):
    def render_param(self, private=False):
        out = self.out
        out << "py::object " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        out << f"static_cast<{self.param.type.spelling}>({param_name}.ptr())"
