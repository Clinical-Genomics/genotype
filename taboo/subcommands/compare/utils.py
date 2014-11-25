# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ..._compat import zip

from toolz import concat
import vcf.utils


def read_vcfs(*streams):
  """Parse multiple sorted streams of VCFs together.

  Uses :function:`vcf.utils.walk_together` to parse multiple VCFs
  together. Also handles VCFs with multiple samples in the same file.

  The output is what is sent to each of the plugins.

  Args:
    streams (list): list of VCF streams to parse

  Yields:
    list of :class:`vcf.model._Call`: -
  """
  # create VCF readers for each stream
  readers = [vcf.Reader(stream) for stream in streams]
  all_samples = list(concat((reader.samples for reader in readers)))

  # iterate the readers in tandem
  positions = vcf.utils.walk_together(*readers)

  # concat samples for each variant
  # FYI: this step will obfuscate when variants are not found in a VCF
  for position in positions:
    variants = []
    for variant, sample in zip(position, all_samples):
      if variant is None:
        variants.append([sample])

      else:
        variants.append(variant.samples)

    yield concat(variants)
