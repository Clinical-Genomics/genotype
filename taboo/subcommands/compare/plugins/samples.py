# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import operator

from ...._compat import text_type

get_gq = operator.attrgetter('data.GQ')


def samples(samples):
  """Get GT type: homozygous, heterzygous etc. for the variant.

  Args:
    samples (list of :class:`vcf.model._Call` instances): one variant

  Returns:
    list: all sample ids
  """
  return (sample if isinstance(sample, text_type) else sample.sample
          for sample in samples)
