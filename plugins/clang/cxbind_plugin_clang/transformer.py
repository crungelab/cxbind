from loguru import logger

from cxbind.unit import Unit
from cxbind.extra import ExtraStandardMethod

from .transform import Mogrify
from .node import FunctionNode, StructuralNode
from .clang_runner import ClangRunner


class MogrifyTransformer:
    """Attach free functions to a structure as methods.

    Every free function whose first parameter is the target type becomes a
    method of it: `b2Body_GetMass(b2Body*)` -> `Body.get_mass()`. The
    function is added as an extra on the structure *node*; the synthesis
    phase turns it into a mogrified clone. The spec is never modified, so
    what the user wrote stays exactly that, and nothing leaks between units
    that share a spec.
    """

    def __init__(self, unit: Unit):
        self.unit = unit

    def transform(self, transform: Mogrify):
        runner = ClangRunner.get_current()

        spec = self.unit.specs.get(transform.target)
        if spec is None:
            raise ValueError(f"Mogrify: no spec for target {transform.target}")

        target = runner.node_registry.get(spec.key)
        if target is None:
            raise ValueError(f"Mogrify: no node for spec {spec.name}")
        if not isinstance(target, StructuralNode):
            raise ValueError(f"Mogrify: {spec.name} is not a class or struct")

        target_pyname = spec.pyname or target.pyname

        existing = {(m.name, m.use) for m in target.extra.methods}
        added = 0

        for node in runner.node_registry:
            if not self.is_candidate(node, spec.name):
                continue

            name = self.method_name(node.pyname, target_pyname)
            if not name:
                logger.warning(
                    f"Mogrify {spec.name}: {node.name} would have an empty method "
                    f"name after stripping '{target_pyname}'; skipped"
                )
                continue

            # Idempotent: a second run (or a second unit transforming the
            # same node) adds nothing. Same name with a different function
            # is kept: that's an overload set, and it's resolved as one.
            if (name, node.key) in existing:
                continue
            existing.add((name, node.key))

            target.extra.add_method(ExtraStandardMethod(name=name, use=node.key))
            added += 1

        logger.debug(f"Mogrify {spec.name}: attached {added} function(s) as methods")

    @staticmethod
    def is_candidate(node, type_name: str) -> bool:
        """A free function whose first parameter is exactly `type_name`.

        Compares the base type (pointers, references and const stripped),
        not a substring: `b2Body` must not match `b2BodyDef*` or `b2BodyId`.
        """
        if not isinstance(node, FunctionNode) or node.mogrified:
            return False
        if not node.params:
            return False
        return node.params[0].type.base_name == type_name

    @staticmethod
    def method_name(function_pyname: str, target_pyname: str) -> str:
        """`body_get_mass` on `Body` -> `get_mass`; also strips a suffix."""
        affix = target_pyname.lower()
        name = function_pyname.removeprefix(affix + "_")
        name = name.removesuffix("_" + affix)
        return name