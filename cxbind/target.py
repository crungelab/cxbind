"""Output targets for a unit.

A unit lists its outputs under ``targets``, keyed by kind:

    targets:
      pb: src/imgui_pb.cpp
      pyi:
        path: crunge/imgui/_imgui.pyi
        template: imgui.pyi

Kinds are shared vocabulary across plugins. A unit only checks that a kind
exists; each plugin decides which kinds it actually supports.
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