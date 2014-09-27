# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import operator

from toolz import pipe, unique
from toolz.curried import map


def gt_type(samples):
  """Get GT type: homozygous, heterzygous etc. for the variant.

  Args:
    samples (list of :class:`vcf.model._Call` instances): one variant

  Returns:
    list: all GT types (only one if fully concordant)
  """
  dictionary = {
    0: 'hom_ref',
    1: 'het',
    2: 'hom_alt',
    None: 'uncalled'
  }

  types = pipe(
    samples,
    map(operator.attrgetter('gt_type')),  # extract all types as ints
    map(dictionary.get),                  # convert to human readable
    list                                  # unwind results
  )

  # merge identical types across all samples
  unique_types = list(unique(types))

  if len(unique_types) == 1:
    # return a single type if they are all the same
    return unique_types

  else:
    # return types for each sample if some discordance
    return types
