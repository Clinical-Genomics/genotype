# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from .core import pipeline


@click.command()
@click.argument('complete_vcf', type=click.File(encoding='utf-8'))
@click.argument('incomplete_vcf', type=click.File(encoding='utf-8'))
def compare(complete_vcf, incomplete_vcf):
  """Compare genotypes in two VCF-files.

  Requires input files to be sorted with the same key!

  COMPLETE_VCF: VCF including all variants with genotypes
  INCOMPLETE_VCF: VCF to compare with (can be subset of variants)
  """
  results = pipeline(complete_vcf, incomplete_vcf)

  click.echo("identical\t%s" % results.get(True, 0))
  click.echo("distinct\t%s" % results.get(False, 0))
