# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import pipeline


@click.command()
@click.argument('maf_file', type=click.Path(exists=True))
@click.argument(
  'vcf_file', type=click.File(encoding='utf-8'), default='-', required=False)
def vcfify(maf_file, vcf_file):
  """Convert a MAF Excel-file to the standard VCF format."""
  for line in pipeline(maf_file, vcf_file):
    click.echo(line)
