import os
import click

from ..cxbind import CxBind

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
      CxBind().gen_all()

@cli.command()
@click.pass_context
@click.argument('name')
def gen(ctx, name):
    CxBind().gen(name)
