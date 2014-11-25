# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import operator

from ...._compat import text_type

get_gq = operator.attrgetter('data.GQ')


def quality(samples):
  """Get GT type: homozygous, heterzygous etc. for the variant.

  Args:
    samples (list of :class:`vcf.model._Call` instances): one variant

  Returns:
    list: all GT types (only one if fully concordant)
  """
  qualities = []
  for sample in samples:

    if isinstance(sample, text_type):
      qualities.append('unknown')

    elif hasattr(sample.data, 'GQ'):
      qualities.append(get_gq(sample))

    else:
      qualities.append('unknown')

  return qualities
