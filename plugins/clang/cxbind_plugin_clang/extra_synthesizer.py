"""Turn each structure's `extra` spec into nodes.

Runs once per unit, after all sources are built and all transforms have run
(transforms may add extras), and before the pyname registry resolves, so
synthesized members take part in name resolution like any other node.
"""

from loguru import logger

from cxbind.entry import EntryKey

from cxbind.extra import (
    ExtraInitMethod,
    ExtraReprMethod,
    ExtraStandardMethod,
    ExtraProperty,
)

from .node import Node, StructuralNode, FieldNode, FunctionalNode
from .extra_node import (
    DefaultInitNode,
    FactoryInitNode,
    ArgsInitNode,
    KwargsInitNode,
    ReprNode,
    PropertyNode,
)
from .pyname_registry import PyKind
from .session import Session


class ExtraSynthesizer:
    def __init__(self, session: Session, node_registry) -> None:
        self.session = session
        self.node_registry = node_registry

    def run(self, roots: list[Node]) -> None:
        # Collect first: synthesis adds children while we'd be traversing.
        structures = [
            node
            for root in roots
            for node in root.traverse()
            if isinstance(node, StructuralNode) and node.spec is not None
        ]
        for structure in structures:
            self.synthesize(structure)

    def synthesize(self, structure: StructuralNode) -> None:
        extra = structure.extra
        for method in extra.methods:
            match method:
                case ExtraInitMethod():
                    self.synthesize_init(structure, method)
                case ExtraReprMethod():
                    self.synthesize_repr(structure, method)
                case ExtraStandardMethod():
                    self.synthesize_method(structure, method)
        for prop in extra.properties:
            self.synthesize_property(structure, prop)

    # --- helpers ---------------------------------------------------------

    @staticmethod
    def direct_fields(structure: StructuralNode) -> list[FieldNode]:
        return [c for c in structure.children if type(c) is FieldNode]

    def lookup(self, structure: StructuralNode, key) -> FunctionalNode:
        node = self.node_registry.get(key)
        if node is None:
            raise ValueError(f"{structure.name}: extra refers to unknown {key}")
        return node

    # --- per kind --------------------------------------------------------

    def synthesize_init(self, structure: StructuralNode, method: ExtraInitMethod) -> None:
        if method.gen_kwargs:
            KwargsInitNode.create(
                structure, "__init__",
                fields=self.direct_fields(structure),
                use=method.use,
                identity=structure.spec.identity,
                origin=method,
            )
        elif method.gen_args:
            ArgsInitNode.create(
                structure, "__init__",
                fields=self.direct_fields(structure),
                origin=method,
            )
        elif method.use is not None:
            self.lookup(structure, method.use)  # fail early on a bad key
            FactoryInitNode.create(structure, "__init__", use=method.use, origin=method)
        else:
            DefaultInitNode.create(structure, "__init__", origin=method)

    def synthesize_repr(self, structure: StructuralNode, method: ExtraReprMethod) -> None:
        fields = self.direct_fields(structure)
        if not method.auto:
            by_name = {f.first_name: f for f in fields}
            missing = [m for m in structure.spec.members if m not in by_name]
            if missing:
                raise ValueError(
                    f"{structure.name}: __repr__ members not found: {', '.join(missing)}"
                )
            fields = [by_name[m] for m in structure.spec.members]
        ReprNode.create(structure, "__repr__", fields=fields, origin=method)

    def synthesize_method(
        self, structure: StructuralNode, method: ExtraStandardMethod
    ) -> None:
        # The used free function, cloned and rendered as a method. Registered
        # now, before resolve, so name collisions are checked like any other.
        clone = self.lookup(structure, method.use).clone()
        clone.mogrified = True
        clone.binding = self.session.pynames.add(
            clone, PyKind.METHOD, structure.binding, method.name, explicit=True
        )
        structure.add_child(clone)

    def accessor_key(self, structure: StructuralNode, ref: str) -> EntryKey:
        """Resolve a property getter/setter reference to an entry key.

        `getX`               -> method@<Structure>::getX  (member of the owner)
        `Properties::getX`   -> method@Properties::getX   (already qualified)
        `function@b2GetMass` -> used as-is                (any explicit key)
        """
        if "@" in ref:
            return EntryKey.parse(ref)
        if "::" in ref:
            return EntryKey.build(kind="method", name=ref)
        return EntryKey.build(kind="method", name=f"{structure.name}::{ref}")

    def resolve_accessor(
        self, structure: StructuralNode, prop: ExtraProperty, role: str, ref: str
    ) -> FunctionalNode:
        key = self.accessor_key(structure, ref)
        node = self.node_registry.get(key)
        if node is None:
            raise ValueError(
                f"{structure.name}: property '{prop.name}' {role} {ref!r} "
                f"not found (looked up {key}); overloaded functions need "
                f"their full key with signature"
            )
        return node

    def synthesize_property(self, structure: StructuralNode, prop: ExtraProperty) -> None:
        getter = self.resolve_accessor(structure, prop, "getter", prop.getter)
        setter = (
            self.resolve_accessor(structure, prop, "setter", prop.setter)
            if prop.setter is not None
            else None
        )
        node = PropertyNode.create(
            structure, prop.name, getter=getter, setter=setter, origin=prop
        )
        # A property is a Python attribute: it must not silently shadow a field.
        node.binding = self.session.pynames.add(
            node, PyKind.FIELD, structure.binding, prop.name, explicit=True
        )
