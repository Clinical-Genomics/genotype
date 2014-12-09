# -*- coding: utf-8 -*-
"""
taboo.cli
~~~~~~~~~

Command line interface (console entry points). Based on Click.
"""
from __future__ import absolute_import, unicode_literals
from pkg_resources import iter_entry_points

import click

from . import __version__


@click.group()
@click.version_option(__version__)
def cli():
  """Provide entry point for VCF genotype comparison utilities."""
  pass


# add subcommands dynamically to the CLI
for entry_point in iter_entry_points('taboo.subcommand'):
  cli.add_command(entry_point.load())
