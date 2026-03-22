from clang import cindex
from loguru import logger

from cxbind.spec import FieldSpec
from cxbind.facade import Facade

from .node_builder import NodeBuilder
from ..node import Node, FieldNode, Type


class FieldBuilder(NodeBuilder[FieldNode]):
    def create_node(self) -> None:
        type = self.build_field_type()
        self.node = FieldNode(kind='field', name=self.name, cursor=self.cursor, type=type)

    def build_node(self):
        super().build_node()
        facade = self.get_field_facade(self.name, self.cursor.type)
        self.node.facade = facade

    def create_pyname(self, name) -> str:
        return self.session.format_field(name)

    def should_cancel(self) -> bool:
        return super().should_cancel() or not self.is_field_bindable(self.cursor)

    def is_field_bindable(self, cursor) -> bool:
        return self.is_cursor_bindable(cursor)

    def build_field_type(
        self,
    ) -> Type:
        field_type: cindex.Type = self.cursor.type
        field_spec: FieldSpec | None = self.lookup_spec(Node.make_key(self.cursor))

        spelling = field_type.spelling
        base_name = self.get_base_type_name(field_type)
        logger.debug(f"Parameter type spelling: {spelling}, base name: {base_name}")

        base_decl = self.get_base_declaration(field_type)
        if base_decl is not None:
            base_key = Node.make_key(base_decl)
            logger.debug(f"Base declaration: {base_decl}")
            logger.debug(f"Base kind: {base_decl.kind}")
            logger.debug(f"Base key: {base_key}")
        else:
            base_key = None

        base_spec = self.lookup_spec(base_key)
        logger.debug(f"base_spec: {base_spec}")

        facade = None
        if field_spec is not None and field_spec.facade is not None:
            facade = field_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return Type(
            spelling=spelling,
            base_name=base_name,
            type=field_type,
            base_spec=base_spec,
            facade=facade,
        )

    def get_field_facade(
        self, field_name: str, field_type: cindex.Type
    ) -> Facade | None:
        node = self.node
        field_spec = self.spec

        base_decl = self.get_base_declaration(field_type)
        if base_decl is not None:
            base_key = Node.make_key(base_decl)
            logger.debug(f"Base declaration: {base_decl}")
            logger.debug(f"Base kind: {base_decl.kind}")
            logger.debug(f"Base key: {base_key}")
        else:
            base_key = None

        base_spec = self.lookup_spec(base_key)
        logger.debug(f"base_spec: {base_spec}")

        facade = None
        if field_spec is not None and field_spec.facade is not None:
            facade = field_spec.facade
        elif base_spec is not None and base_spec.facade is not None:
            facade = base_spec.facade

        return facade
