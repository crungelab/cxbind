import os
import click
import json

from .compiler import Compiler

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
      Compiler().run()
