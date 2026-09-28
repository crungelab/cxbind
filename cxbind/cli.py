from typing import Callable
import sys

import click
from loguru import logger

from .cxbind import CxBind, CxBindError

LOG_FILE = "_cxbind/cxbind.log"
LOG_FORMAT = "<level>{level: <8}</level> | {file}:{line: >4} - {message}"



def configure_logging(verbose: bool = False) -> None:
    logger.remove()  # drop loguru's default DEBUG-to-stderr sink
    logger.add(sys.stderr, level="DEBUG" if verbose else "WARNING")
    logger.add(
        LOG_FILE,
        mode="w",
        level="DEBUG",
        format=LOG_FORMAT,
        colorize=False,
        backtrace=True,
        diagnose=True,
    )

def run(action: Callable[[CxBind], None]) -> None:
    """Run a CxBind action, turning its errors into a clean CLI failure."""
    try:
        action(CxBind())
    except CxBindError as e:
        raise click.ClickException(str(e)) from None


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Generate bindings for the project in the current directory.

    With no command, generates every unit.
    """
    configure_logging()
    if ctx.invoked_subcommand is None:
        run(lambda cxbind: cxbind.gen_all())


@cli.command()
@click.argument("name")
def gen(name: str) -> None:
    """Generate a single unit."""
    run(lambda cxbind: cxbind.gen(name))