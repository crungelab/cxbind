"""Output targets for a unit.

Targets are keyed by kind and may be set on the project, the unit, or both:

    # project
    targets:
      pb: 'src/{name}_py_auto.cpp'
      pyi: 'tests.pyi'

    # unit
    targets:
      pyi: null          # opt out of an inherited target
      pb:
        path: 'src/special.cpp'
        template: 'special.cpp'

Paths and templates may use {name} and {module}, expanded per unit when
targets are merged. Kinds are shared vocabulary across plugins; each plugin
decides which kinds it actually supports.
"""

from pathlib import PurePath
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

_registry: dict[str, type["Target"]] = {}


class Target(BaseModel):
    kind: ClassVar[str] = ""

    path: str
    template: str | None = None

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        kind = cls.__dict__.get("kind")
        if not kind:
            return
        existing = _registry.get(kind)
        if existing is not None and existing is not cls:
            raise TypeError(
                f"Target kind {kind!r} already registered by {existing.__name__}"
            )
        _registry[kind] = cls

    def expand(self, **fields: Any) -> "Target":
        """Copy with {placeholders} in path and template filled in."""

        def fmt(value: str | None) -> str | None:
            if value is None:
                return None
            try:
                return value.format(**fields)
            except KeyError as e:
                raise ValueError(
                    f"targets.{self.kind}: unknown placeholder {e} in {value!r} "
                    f"(available: {', '.join(fields)})"
                ) from None

        return self.model_copy(
            update={"path": fmt(self.path), "template": fmt(self.template)}
        )


class PbTarget(Target):
    """pybind11 binding source."""

    kind: ClassVar[str] = "pb"


class PyiTarget(Target):
    """Python type stub."""

    kind: ClassVar[str] = "pyi"


class HppTarget(Target):
    """C++ wrapper header."""

    kind: ClassVar[str] = "hpp"


class CppTarget(Target):
    """C++ wrapper source."""

    kind: ClassVar[str] = "cpp"


class PyTarget(Target):
    """Generated Python source (e.g. dataclasses)."""

    kind: ClassVar[str] = "py"


def get_target_class(kind: str) -> type[Target] | None:
    return _registry.get(kind)


def target_kinds() -> list[str]:
    return list(_registry)


def dispatch_targets(v: Any) -> dict[str, Target | None]:
    """Validate a raw `targets` mapping into Target subclasses.

    A value of None is kept: it marks an inherited target as removed.
    """
    if v is None:
        return {}
    if not isinstance(v, dict):
        raise TypeError("targets must be a mapping of kind -> target")

    out: dict[str, Target | None] = {}
    for kind, raw in v.items():
        target_cls = get_target_class(kind)
        if target_cls is None:
            raise ValueError(
                f"Unknown target {kind!r} (known: {', '.join(target_kinds())})"
            )

        if raw is None or isinstance(raw, Target):
            out[kind] = raw
            continue
        if isinstance(raw, str):
            raw = {"path": raw}  # shorthand: `pyi: src/wgpu.pyi`
        elif not isinstance(raw, dict):
            raise TypeError(f"targets.{kind} must be a path, an object, or null")

        out[kind] = target_cls.model_validate(raw)
    return out


def merge_targets(
    inherited: dict[str, Target | None],
    own: dict[str, Target | None],
    **fields: Any,
) -> dict[str, Target]:
    """Unit targets override project targets per kind; None removes one.

    The result has placeholders expanded and no None entries.
    """
    merged = {**inherited, **own}
    return {
        kind: target.expand(**fields)
        for kind, target in merged.items()
        if target is not None
    }


# Legacy single-target unit files only have a path, so the kind is guessed
# from the extension. ".cpp" is ambiguous (pb vs cpp) and defaults to pb.
_LEGACY_KIND_BY_SUFFIX = {
    ".pyi": "pyi",
    ".py": "py",
    ".hpp": "hpp",
    ".h": "hpp",
}


def infer_legacy_kind(path: str) -> str:
    return _LEGACY_KIND_BY_SUFFIX.get(PurePath(path).suffix, "pb")