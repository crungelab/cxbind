from typing import Any, List, Optional

from typing_extensions import Annotated
from pydantic import BeforeValidator, field_validator, model_validator
from loguru import logger

from .unit_base import UnitBase
from .transform import Transform, _registry as TRANSFORM_REGISTRY
from .target import Target, infer_legacy_kind


class Unit(UnitBase):
    source: Optional[str] = None
    sources: Optional[List[str]] = []
    mapped: Optional[List[str]] = []
    transforms: list[Transform] = []
    generate: bool = True
    internal: bool = False

    # --- validation ------------------------------------------------------

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_target(cls, data: Any) -> Any:
        """Old unit files: top-level `target:` (+ `template:`) becomes one entry in `targets`.

        Runs before field validation so extra="forbid" never sees the legacy keys.
        """
        if not isinstance(data, dict):
            return data
        if "target" not in data and "template" not in data:
            return data

        data = dict(data)
        path = data.pop("target", None)
        template = data.pop("template", None)
        targets = dict(data.get("targets") or {})

        if path is not None:
            kind = infer_legacy_kind(path)
            if kind in targets:
                raise ValueError(
                    f"unit {data.get('name')!r}: legacy 'target' conflicts with "
                    f"targets.{kind}; use one or the other"
                )
            legacy: dict[str, Any] = {"path": path}
            if template is not None:
                legacy["template"] = template
            targets[kind] = legacy
        elif template is not None:
            logger.warning(
                f"unit {data.get('name')!r}: 'template' without 'target' is ignored; "
                f"set it on a target instead"
            )

        data["targets"] = targets
        return data

    @model_validator(mode="after")
    def handle_internal_logic(self) -> "Unit":
        if self.internal:
            self.generate = False
        return self

    @field_validator("transforms", mode="before")
    @classmethod
    def dispatch_transforms(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise TypeError("transforms must be a list")

        out = []
        for i, raw in enumerate(v):
            logger.debug(f"dispatch_transforms: raw[{i}] = {raw}")
            if isinstance(raw, Transform):
                out.append(raw)
                continue
            if not isinstance(raw, dict):
                raise TypeError(f"transforms[{i}] must be an object/dict")

            t = raw.get("name")
            model_cls = TRANSFORM_REGISTRY.get(t)
            if model_cls is None:
                raise ValueError(f"Unknown name {t!r} at transforms[{i}]")

            out.append(model_cls.model_validate(raw))
        return out

    # --- compat (remove once dawn reads `targets`) -----------------------

    def _single_target(self) -> Target | None:
        active = {k: t for k, t in self.targets.items() if t is not None}
        if len(active) == 1:
            return next(iter(active.values()))
        return active.get("pb")

    @property
    def target(self) -> str | None:
        """Deprecated: path of the unit's only target (or its pb target)."""
        t = self._single_target()
        return t.path if t else None

    @property
    def template(self) -> str | None:
        """Deprecated: template of the unit's only target (or its pb target)."""
        t = self._single_target()
        return t.template if t else None


def validate_unit_dict(v: dict[str, Unit]) -> dict[str, Unit]:
    for key, value in v.items():
        value["name"] = key
    return v


UnitDict = Annotated[dict[str, Unit], BeforeValidator(validate_unit_dict)]