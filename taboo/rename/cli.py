# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import pipeline


@click.command()
@click.option('--remove', default='ID-')
@click.argument('samples_json', type=click.File(encoding='utf-8'))
@click.argument(
  'vcf_file', type=click.File(encoding='utf-8'), default='-', required=False)
def rename(samples_json, vcf_file, remove):
  """Convert sample names using mapping information in a JSON file."""
  for line in pipeline(vcf_file, samples_json, remove_string=remove):
    click.echo(line)
