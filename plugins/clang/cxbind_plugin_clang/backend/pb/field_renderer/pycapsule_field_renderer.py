from cxbind.facade import PyCapsuleFacade

from ...renderer_registry import RendererRegistry

from .field_renderer import FacadeFieldRenderer


@RendererRegistry.register("field", "pycapsule")
class PyCapsuleFieldRenderer(FacadeFieldRenderer[PyCapsuleFacade]):
    def render(self):
        node = self.node
        cursor = node.cursor
        pname = self.top_node.name
        name = cursor.spelling
        pyname = node.pyname
        field_type_name = self.get_base_type_name(cursor.type)

        result = f'py::capsule(self.{name}, "{field_type_name}")'
        value = f"const py::capsule& value"

        self.begin_chain()

        self.out("//render_pycapsule_field")
        self.out(f'.def_property("{pyname}",')
        with self.out:
            self.out(f"[](const {pname}& self)" "{" f" return {result};" " },")
            self.out(f"[]({pname}& self, {value})" "{" f" self.{name} = value;" " }")
        self.out(")")
