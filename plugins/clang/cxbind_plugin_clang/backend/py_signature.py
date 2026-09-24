from dataclasses import dataclass
from typing import Callable

from clang import cindex

from ..node import FunctionalNode, Parameter


@dataclass(frozen=True)
class PyParam:
    param: Parameter
    name: str  # Python-side name

    @property
    def has_default(self) -> bool:
        return self.param.default is not None

    @property
    def is_out(self) -> bool:
        # Out params are in-out from Python: passed in, and returned.
        return self.param.is_out


@dataclass(frozen=True)
class PySignature:
    """What Python sees for a function or method.

    Both backends read this instead of deciding for themselves, so the
    binding and the stub can't disagree.
    """

    node: FunctionalNode
    params: list[PyParam]      # visible to Python, in order; mogrified self skipped
    excluded: frozenset[str]   # C++ params hidden from Python (facade companions)
    out_params: list[Parameter]
    is_void: bool
    returns_value: bool        # does the C++ return value reach Python?

    @property
    def has_out_params(self) -> bool:
        return bool(self.out_params)

    @property
    def outputs(self) -> int:
        return (1 if self.returns_value else 0) + len(self.out_params)

    @property
    def returns_tuple(self) -> bool:
        return self.outputs >= 2

    @classmethod
    def from_node(
        cls, node: FunctionalNode, format_field: Callable[[str], str]
    ) -> "PySignature":
        excluded: set[str] = set()
        for param in node.params:
            facade = param.type.facade
            if facade is not None:
                excluded |= facade.excluded_params()

        visible = [p for p in node.params if p.name not in excluded]
        if node.mogrified:
            visible = visible[1:]

        out_params = [p for p in node.params if p.is_out]
        is_void = node.cursor.type.get_result().kind == cindex.TypeKind.VOID
        # omit_ret only applies when out params are present; otherwise the
        # return value always goes back to Python.
        returns_value = not is_void and not (out_params and node.spec.omit_ret)

        return cls(
            node=node,
            params=[PyParam(p, format_field(p.name)) for p in visible],
            excluded=frozenset(excluded),
            out_params=out_params,
            is_void=is_void,
            returns_value=returns_value,
        )