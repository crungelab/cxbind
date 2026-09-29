from typing import Callable
import sys

import click
from loguru import logger

from .cxbind import CxBind, CxBindError
from .outputs import Outputs
from .report import REPORT_NAME

LOG_FILE = "_cxbind/cxbind.log"
REPORT_FILE = f"_cxbind/{REPORT_NAME}"
LOG_FORMAT = "<level>{level: <8}</level> | {file}:{line: >4} - {message}"


def configure_logging(verbose: bool = False) -> None:
    logger.remove()  # drop loguru's default DEBUG-to-stderr sink
    # sys.stderr is looked up at each write, not captured here: while a progress bar is
    # up, rich swaps it for a wrapper that prints above the bar. A captured stream would
    # write through the bar and leave a frozen frame behind.
    logger.add(
        lambda message: sys.stderr.write(message),
        level="DEBUG" if verbose else "WARNING",
        colorize=sys.stderr.isatty(),
    )
    logger.add(
        LOG_FILE,
        mode="w",
        level="DEBUG",
        format=LOG_FORMAT,
        colorize=False,
        backtrace=True,
        diagnose=True,
    )


def run(action: Callable[[CxBind], Outputs], check: bool = False) -> None:
    """Run a CxBind action, turning its errors (and, with --check, stale files) into a CLI failure."""
    try:
        outputs = action(CxBind())
    except CxBindError as e:
        raise click.ClickException(str(e)) from None
    if check and (stale := outputs.out_of_date):
        raise click.ClickException(
            f"{len(stale)} generated file(s) out of date; run cxbind to regenerate them "
            f"(what would change: {REPORT_FILE})"
        )


CHECK_HELP = "Write nothing; fail if generating would change any file."


@click.group(invoke_without_command=True)
@click.option("--check", is_flag=True, help=CHECK_HELP)
@click.pass_context
def cli(ctx: click.Context, check: bool) -> None:
    """Generate bindings for the project in the current directory.

    With no command, generates every unit.
    """
    configure_logging()
    ctx.ensure_object(dict)["check"] = check
    if ctx.invoked_subcommand is None:
        run(lambda cxbind: cxbind.gen_all(check=check), check)


@cli.command()
@click.argument("name")
@click.option("--check", is_flag=True, help=CHECK_HELP)
@click.pass_context
def gen(ctx: click.Context, name: str, check: bool) -> None:
    """Generate a single unit."""
    check = check or ctx.obj.get("check", False)  # `cxbind --check gen X` works too
    run(lambda cxbind: cxbind.gen(name, check=check), check)
