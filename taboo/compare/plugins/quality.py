# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import operator

get_gq = operator.attrgetter('data.GQ')


def quality(samples):
  """Get GT type: homozygous, heterzygous etc. for the variant.

  Args:
    samples (list of :class:`vcf.model._Call` instances): one variant

  Returns:
    list: all GT types (only one if fully concordant)
  """
  return [get_gq(sample) if hasattr(sample.data, 'GQ') else None
          for sample in samples]
