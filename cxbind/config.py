"""Directory-scoped cxbind settings, EditorConfig-style.

cxbind searches upward from the working directory for `.cxbind/`
directories. Each may hold:

    .cxbind/config.yaml   settings; nearer files override farther ones
    .cxbind/templates/    templates; nearer directories are searched first

The search stops at the repository root (a directory containing `.git`)
or at a config with `root: true`, so settings never leak in from outside
the project.

Relative paths in a config resolve against the directory that contains
its `.cxbind/`, not the working directory, so an inherited setting means
the same thing from every subfolder.
"""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from pydantic import BaseModel, ConfigDict

CONFIG_DIR = ".cxbind"
CONFIG_FILE = "config.yaml"
TEMPLATES_DIR = "templates"

# Settings holding paths, resolved relative to their config's location.
PATH_KEYS = ("pyi_copy",)


class CxbindConfig(BaseModel):
    # Stop searching further up once this config is found.
    root: bool = False

    # Mirror every generated .pyi to this path pattern (placeholders:
    # {stem} = stub filename without extension, {module} = unit module).
    # Example: typings/cxbind_tests/test_{stem}.pyi
    pyi_copy: str | None = None

    model_config = ConfigDict(extra="forbid")


def _read(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping of settings")
    return data


def find_config_dirs(start: Path | None = None) -> list[Path]:
    """`.cxbind` directories from start upward, nearest first."""
    start = (start or Path.cwd()).resolve()
    found: list[Path] = []
    for directory in [start, *start.parents]:
        candidate = directory / CONFIG_DIR
        if candidate.is_dir():
            found.append(candidate)
            config = candidate / CONFIG_FILE
            if config.is_file() and _read(config).get("root"):
                break
        if (directory / ".git").exists():
            break
    return found


def template_dirs(start: Path | None = None) -> list[Path]:
    """`.cxbind/templates` directories from start upward, nearest first."""
    return [
        d / TEMPLATES_DIR
        for d in find_config_dirs(start)
        if (d / TEMPLATES_DIR).is_dir()
    ]


def load_config(start: Path | None = None) -> CxbindConfig:
    merged: dict[str, Any] = {}
    # Farthest first, so nearer configs override per setting.
    for cxbind_dir in reversed(find_config_dirs(start)):
        config = cxbind_dir / CONFIG_FILE
        if not config.is_file():
            continue
        data = _read(config)
        for key in PATH_KEYS:
            if data.get(key):
                # Relative to the directory holding this .cxbind/.
                data[key] = str(cxbind_dir.parent / Path(data[key]).expanduser())
        logger.debug(f"cxbind config: {config}")
        merged.update(data)
    return CxbindConfig.model_validate(merged)
