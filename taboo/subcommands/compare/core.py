# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import itertools
from pkg_resources import iter_entry_points

from toolz import cons

from ..._compat import text_type, zip
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
  sample_ids = kwargs.get('samples', None)

  if sample_ids is not None:
    sample_ids = set(sample_ids)

  # load all requested comparators via entry point system
  # if "plugins" is ``None``, load all installed plugins
  entry_points = [entry_point
                  for entry_point in iter_entry_points('taboo.comparator')
                  if (plugins is None) or (entry_point.name in plugins)]

  comparators = [entry_point.load() for entry_point in entry_points]

  # the name value is not unicode so I need to convert ASAP
  columns = (text_type(entry_point.name) for entry_point in entry_points)
  first_column = "#%s" % next(columns)
  yield cons(first_column, columns)

  # loop over each variant position covered across the VCF streams
  for samples in read_vcfs(*streams):

    # pick out what samples to include
    included_samples = [sample for sample in samples
                        if sample_ids is None or sample.sample in sample_ids]

    # make enough independent iterators to cover all comparators
    samples_copies = itertools.tee(included_samples, len(comparators))

    # run each comparator on one of the samples copies
    yield [comparator(samples_copy)
           for comparator, samples_copy in zip(comparators, samples_copies)]
