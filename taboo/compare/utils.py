# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

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

  # iterate the readers in tandem
  combo_sequence = vcf.utils.walk_together(*readers)

  # concat samples for each variant
  # FYI: this step will obfuscate when variants are not found in a VCF
  return (concat(variant.samples for variant in combo if variant)
          for combo in combo_sequence)
