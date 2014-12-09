# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import collections

import click

from ..._compat import text_type
from .core import compare_vcfs


@click.command()
@click.option('-p', '--plugins', type=str, default=None)
@click.option('-s', '--samples', type=str, default=None,
              help='List of samples to check')
@click.argument('vcfs', nargs=-1, type=click.File(encoding='utf-8'),
                required=True)
def compare(plugins, samples, vcfs):
  """Compare genotypes in two VCF-files.

  Requires input files to be sorted with the same key.

  VCFS: VCFs including any number of samples
  """
  if plugins:
    plugins = plugins.split(',')

  # make into python list
  if samples:
    samples = samples.split(',')

  for variant_results in compare_vcfs(*vcfs, plugins=plugins, samples=samples):

    click.echo('\t'.join(map(stringify, variant_results)))


def stringify(item, delimiter=','):
  """Serialize various objects to string format.

  Args:
    item (multiple): ``list``, ``str``, or some other object
    delimiter (str, optional): separator to serialize lists

  Returns:
    str: serialized version of the ``item``
  """
  if isinstance(item, text_type):
    return item

  elif isinstance(item, collections.Iterable):
    return delimiter.join(map(text_type, item))

  else:
    return text_type(item)
