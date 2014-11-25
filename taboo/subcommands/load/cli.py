# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import load_comparison


@click.command()
@click.argument('compare_output', type=click.File(encoding='utf-8'),
                default='-', required=False)
@click.option('-u', '--uri', default=':memory:')
@click.option('-d', '--dialect', default='sqlite')
def load(compare_output, uri, dialect):
  """Extract the most interesting information from a VCF-file."""
  load_comparison(compare_output, uri=uri, dialect=dialect)
