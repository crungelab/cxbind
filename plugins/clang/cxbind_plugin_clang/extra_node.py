"""Nodes synthesized from a structure's `extra` spec.

These have no C++ counterpart, so they subclass Node, not DeclNode: there is
no cursor to rely on. Everything a renderer needs is resolved once, when the
node is synthesized, and stored on the node, so backends read the tree and
never the spec.

Mapping from extra.py:

    ExtraInitMethod (plain)        -> DefaultInitNode    py::init<>()
    ExtraInitMethod (use)          -> FactoryInitNode    py::init(&factory)
    ExtraInitMethod (gen_args)     -> ArgsInitNode       positional fields
    ExtraInitMethod (gen_kwargs)   -> KwargsInitNode     keyword fields (+ use)
    ExtraReprMethod                -> ReprNode
    ExtraProperty                  -> PropertyNode
    ExtraStandardMethod            -> a clone of the used FunctionNode with
                                      mogrified=True (no new node kind)
"""

from typing import Literal

from pydantic import Field

from cxbind.entry import EntryKey
from cxbind.extra import Extra, ExtraInitMethod, ExtraReprMethod, ExtraProperty

from .node import Node, FieldNode, FunctionalNode


class ExtraNode(Node):
    # The spec entry this node came from, for error messages. Kept apart
    # from `spec` so code reading node.spec always gets a real Spec.
    origin: Extra | ExtraInitMethod | ExtraReprMethod | ExtraProperty | None = Field(
        None, exclude=True, repr=False
    )

    @classmethod
    def create(cls, owner: Node, member: str, **kwargs) -> "ExtraNode":
        """Synthesize a member of `owner` and attach it as a child.

        The name is qualified like a real node's (`Owner::member`), so
        `first_name` is the member name and `key` stays unique, e.g.
        `kwargs_init@b2DistanceJointDef::__init__`.
        """
        node = cls(name=f"{owner.name}::{member}", **kwargs)
        owner.add_child(node)
        return node


# --- __init__ ---------------------------------------------------------------


class InitNode(ExtraNode):
    """Base for every synthesized __init__ variant."""


class DefaultInitNode(InitNode):
    kind: Literal["default_init"] = "default_init"


class FactoryInitNode(InitNode):
    kind: Literal["factory_init"] = "factory_init"
    use: EntryKey


class ArgsInitNode(InitNode):
    kind: Literal["args_init"] = "args_init"
    # The structure's own fields, in declaration order. References, not
    # children: they already belong to the structure.
    fields: list[FieldNode] = Field(default_factory=list, exclude=True, repr=False)


class KwargsInitNode(InitNode):
    kind: Literal["kwargs_init"] = "kwargs_init"
    fields: list[FieldNode] = Field(default_factory=list, exclude=True, repr=False)
    # Where the object starts before kwargs are applied, in priority order:
    # a factory function, the structure's identity expression, or `T{}`.
    use: EntryKey | None = None
    identity: str | None = None


# --- __repr__ ---------------------------------------------------------------


class ReprNode(ExtraNode):
    kind: Literal["repr"] = "repr"
    # Fields shown, already chosen: all of them for `auto`, else spec.members.
    fields: list[FieldNode] = Field(default_factory=list, exclude=True, repr=False)


# --- properties -------------------------------------------------------------


class PropertyNode(ExtraNode):
    kind: Literal["property"] = "property"
    # Resolved accessor functions (methods, or free functions taking the
    # structure first). References, not children: they belong elsewhere.
    getter: FunctionalNode = Field(exclude=True, repr=False)
    setter: FunctionalNode | None = Field(None, exclude=True, repr=False)

    @property
    def readonly(self) -> bool:
        return self.setter is None
