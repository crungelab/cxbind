from cxbind.facade import WrapperFacade

from ...renderer_registry import RendererRegistry

from .field_renderer import FacadeFieldRenderer


@RendererRegistry.register("field", "wrapper")
class WrapperFieldRenderer(FacadeFieldRenderer[WrapperFacade]):
    def render(self):
        node = self.node
        cursor = node.cursor
        pname = self.top_node.name
        name = cursor.spelling
        pyname = node.pyname
        field_type_name = self.get_base_type_name(cursor.type)

        wrapper = self.wrapped[field_type_name].wrapper
        result = f"{wrapper}(self.{name})"
        value = f"const {wrapper}& value"

        self.out("//render_wrapper_field")
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[](const {pname}& self)" "{" f" return {result};" " },")
            self.out(f"[]({pname}& self, {value})" "{" f" self.{name} = value;" " }")
        self.out(")")
