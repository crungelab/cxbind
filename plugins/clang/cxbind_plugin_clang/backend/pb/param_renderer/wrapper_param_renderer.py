from cxbind.facade import WrapperFacade

from .param_renderer import FacadeParamRenderer


class WrapperParamRenderer(FacadeParamRenderer[WrapperFacade]):
    def render_param(self, private=False):
        out = self.out
        out << f"{self.facade.wrapper} " << self.param.name

    def render_arg(self):
        out = self.out
        param_name = self.param.name
        out << f"static_cast<{self.param.type.spelling}>({param_name}.get())"
