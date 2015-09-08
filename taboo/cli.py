# -*- coding: utf-8 -*-
"""
taboo.cli
~~~~~~~~~
Command line interface (console entry points). Based on Click.
Loads subcommands dynamically using setuptools entry points.
"""
from __future__ import absolute_import, unicode_literals
from pkg_resources import iter_entry_points

import click

import taboo
import taboo.store


@click.group()
@click.version_option(taboo.__version__)
@click.option('-d', '--db-path', type=click.Path(), default='./taboo.sqlite3')
@click.pass_context
def cli(context, db_path):
    """Genotype comparison tool."""
    context.store = taboo.store.Database(db_path)


# add subcommands dynamically to the CLI
for entry_point in iter_entry_points('taboo.subcommand'):
    cli.add_command(entry_point.load())
