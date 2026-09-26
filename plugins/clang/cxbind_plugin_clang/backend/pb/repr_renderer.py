from loguru import logger

from ...node import StructuralNode
from ...extra_node import ReprNode

from ..renderer_registry import PbRendererRegistry
from .node_renderer import NodeRenderer


@PbRendererRegistry.register("repr")
class ReprRenderer(NodeRenderer[ReprNode]):
    def render(self):
        structure: StructuralNode = self.node.parent
        logger.debug(f"rendering __repr__ for: {structure.name}")
        self.begin_chain()

        self.out(f'.def("__repr__", [](const {structure.name} &self) {{')
        with self.out:
            self.out("std::stringstream ss;")
            self.out(f'ss << "{structure.pyname}(";')

            for i, field in enumerate(self.node.fields):
                if i > 0:
                    self.out('ss << ", ";')
                if field.type.base_name == "py::function":
                    self.out(
                        f'ss << "{field.first_name}=" << py::repr(self.{field.first_name}).cast<std::string>();'
                    )
                else:
                    self.out(
                        f'ss << "{field.first_name}=" << py::repr(py::cast(self.{field.first_name})).cast<std::string>();'
                    )

            self.out('ss << ")";')
            self.out("return ss.str();")
        self.out("})")
