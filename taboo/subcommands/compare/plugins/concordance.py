# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import itertools
import operator

from toolz import complement, curry, isdistinct, pipe
from toolz.curried import groupby, map, valmap

from ...._compat import text_type

get_alleles = operator.attrgetter('gt_alleles')


@curry
def combinations(sequence, r=2):
  """Find all possible combinations of items in a sequence.

  Curried version of :function:`itertools.combinations`. Doesn't take
  into account repeated combinations.

  Args:
    sequence (iterable): list of any objects
    r (int, optional): number of items in each combination, default: 2

  Returns:
    list of tuple: list of all combinations as tuples
  """
  return itertools.combinations(sequence, r)


def concordance(samples):
  """Determine genotype identity between samples.

  For variants only found in a single sample, ``None`` is returned
  instead of a boolean value. Handle this downstream.

  Args:
    samples: list of :class:`vcf.model._Call` instances

  Returns:
    bool or None: weather all genotypes are identical, None if only one
      sample in comparison
  """
  try:
    results = pipe(
      (sample for sample in samples if not isinstance(sample, text_type)),
      map(get_alleles),             # get alleles (ex: 0/1)
      map(set),                     # reduce homozyg. + normalize "order"
      map(''.join),                 # enable comparison
      combinations(r=2),            # consider all combos
      map(complement(isdistinct)),  # check whether all combos are equal
      groupby(operator.truth),      # filter out all non-equal results
      valmap(len),                  # count identical/different calls
    )

  except AttributeError:
    # one of the genotypes was a failed call, i.e. "./."
    results = {}

  if False in results:
    # one of the comparisons was not identical
    return 'discordant'

  elif True in results:
    # all comparisons where identical
    return 'concordant'

  else:
    # needs genotypes for more than a *single sample* to compare
    return 'unknown'
