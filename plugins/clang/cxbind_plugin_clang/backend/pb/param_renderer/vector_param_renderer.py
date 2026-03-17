from cxbind.facade import VectorFacade

from ....node import Parameter

from .param_renderer import FacadeParamRenderer

class VectorParamRenderer(FacadeParamRenderer[VectorFacade]):
    def __init__(self, param: Parameter):
        super().__init__(param)
        self.length_param = self.facade.length_param

    def excludes(self) -> set[str]:
        return {self.length_param}

    def render_param(self, private=False):
        out = self.out
        # out << f"std::vector<{self.param.type.spelling}> " << self.param.name
        out << f"std::vector<{self.param.type.base_name}> " << self.param.name

    def render_arg(self, private=False) -> None:
        super().render_arg(private=True)

    def render(self):
        out = self.out
        param_name = self.param.name
        param_type = self.param.type
        value = f"""\
        {param_type.spelling} _{param_name} = ({param_type.spelling}){param_name}.data();
        auto {self.length_param} = {param_name}.size();
        """
        out(value)
