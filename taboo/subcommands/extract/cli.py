# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import pipeline


@click.command()
@click.argument('rsnumbers_file', type=click.File(encoding='utf-8'))
@click.argument('vcf_file', type=click.File(encoding='utf-8'), default='-',
                required=False)
def extract(rsnumbers_file, vcf_file):
  """Extract variants matching a list of RS numbers."""
  for line in pipeline(vcf_file, rsnumbers_file):
    click.echo(line)
