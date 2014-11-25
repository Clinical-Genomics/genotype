# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ...._compat import text_type


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

  # extract all types as ints, then convert to human readable strings
  types = []
  for sample in samples:
    if isinstance(sample, text_type):
      gt_key = None
    else:
      gt_key = sample.gt_type

    types.append(dictionary.get(gt_key))

  # return types for each sample if some discordance
  return types
