import shutil
from dataclasses import dataclass, field
from pathlib import Path

import jinja2
from loguru import logger
from rich import print

from cxbind.config import CxbindConfig, load_config
from cxbind.runner.phase import AssemblyPhase
from cxbind.runner.task import LambdaTask

# (module, name); name None means a plain `import module`.
Import = tuple[str, str | None]


@dataclass
class StubFragment:
    unit: str
    module: str | None
    body: str
    template: jinja2.Template
    imports: set[Import] = field(default_factory=set)


class StubAssembler:
    """Merges every unit's stub fragment for a path into one .pyi.

    A module has exactly one stub, but several units can compile into the
    same module. Units that share a pyi target path are merged here, after
    all units have generated.
    """

    def __init__(self, config: CxbindConfig) -> None:
        self.config = config
        self.fragments: dict[str, list[StubFragment]] = {}

    @classmethod
    def for_runner(cls, runner) -> "StubAssembler":
        # One assembler per runner; the first pyi backend creates it and
        # schedules the single assembly task.
        assembler = getattr(runner, "_stub_assembler", None)
        if assembler is None:
            assembler = cls(load_config())
            runner._stub_assembler = assembler
            runner.plan.get_phase(AssemblyPhase).add_task(LambdaTask(assembler.assemble))
        return assembler

    def add(self, path: str, fragment: StubFragment) -> None:
        self.fragments.setdefault(path, []).append(fragment)

    def assemble(self) -> None:
        for path, fragments in self.fragments.items():
            self.assemble_one(Path(path), fragments)
        self.fragments.clear()

    def assemble_one(self, path: Path, fragments: list[StubFragment]) -> None:
        units = ", ".join(f.unit for f in fragments)

        modules = {f.module for f in fragments}
        if len(modules) > 1:
            raise ValueError(
                f"{path}: units ({units}) disagree on module: {sorted(map(str, modules))}"
            )

        templates = {f.template.name for f in fragments}
        if len(templates) > 1:
            raise ValueError(
                f"{path}: units ({units}) use different templates: {sorted(templates)}"
            )

        imports: set[Import] = set()
        for f in fragments:
            imports |= f.imports

        # One blank line between units; empty fragments leave no gap.
        body = "\n\n".join(f.body.strip("\n") for f in fragments if f.body.strip())
        rendered = fragments[0].template.render(
            {"imports": render_imports(imports), "body": body}
        )
        if not rendered.endswith("\n"):
            rendered += "\n"

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            fh.write(rendered)

        if len(fragments) > 1:
            logger.debug(f"{path}: merged stubs from {units}")
        print(f"[bold green]Generated[/bold green]: {path}", ":thumbs_up:")

        self.copy_stub(path, fragments[0].module)

    def copy_stub(self, path: Path, module: str | None) -> None:
        """Mirror the stub per .cxbind/config.yaml `pyi_copy`, if set."""
        pattern = self.config.pyi_copy
        if not pattern:
            return
        try:
            dest = Path(pattern.format(stem=path.stem, module=module))
        except KeyError as e:
            raise ValueError(
                f"pyi_copy: unknown placeholder {e} in {pattern!r} (available: stem, module)"
            ) from None
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        logger.debug(f"Copied {path} -> {dest}")


def render_imports(imports: set[Import]) -> str:
    plain = sorted(module for module, name in imports if name is None)
    grouped: dict[str, set[str]] = {}
    for module, name in imports:
        if name is not None:
            grouped.setdefault(module, set()).add(name)

    lines = [f"import {module}" for module in plain]
    lines += [
        f"from {module} import {', '.join(sorted(names))}"
        for module, names in sorted(grouped.items())
    ]
    return "\n".join(lines)
