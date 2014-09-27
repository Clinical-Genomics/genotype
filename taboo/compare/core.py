# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import itertools
from pkg_resources import iter_entry_points

from .._compat import text_type, zip
from .utils import read_vcfs


def compare_vcfs(*streams, **kwargs):
  """Compare multiple samples in VCF files using a set of comparators.

  Args:
    \*stream (iterable): VCF file stream
    plugins (list of str): names of plugin comparators to use

  Yields:
    list: output from each plugin for a single variant position
  """
  # replicate common kwarg functionality with default value
  plugins = kwargs.get('plugins', ['identity', 'concordance'])

  # load all requested comparators via entry point system
  # if "plugins" is ``None``, load all installed plugins
  entry_points = [entry_point
                  for entry_point in iter_entry_points('taboo.comparator')
                  if (plugins is None) or (entry_point.name in plugins)]

  comparators = [entry_point.load() for entry_point in entry_points]

  # yield first line as a header
  # the name value is not unicode so I need to convert ASAP
  yield [text_type(entry_point.name) for entry_point in entry_points]

  # loop over each variant position covered across the VCF streams
  for samples in read_vcfs(*streams):

    # make enough independent iterators to cover all comparators
    samples_copies = itertools.tee(samples, len(comparators))

    # run each comparator on one of the samples copies
    yield [comparator(samples_copy)
           for comparator, samples_copy in zip(comparators, samples_copies)]
