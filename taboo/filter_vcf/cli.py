# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import pipeline


@click.command('filter')
@click.argument(
  'vcf_file', type=click.File(encoding='utf-8'), default='-', required=False)
def filter_vcf(vcf_file):
  """Extract the most interesting information from a VCF-file."""
  for line in pipeline(vcf_file):
    click.echo(line)
