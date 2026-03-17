from cxbind.facade import PyCapsuleFacade

from .param_renderer import FacadeParamRenderer

class PyCapsuleParamRenderer(FacadeParamRenderer[PyCapsuleFacade]):
    def render_param(self, private=False):
        out = self.out
        out << "py::capsule " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        (out << f"static_cast<{self.param.type.spelling}>({param_name}.get_pointer())")
