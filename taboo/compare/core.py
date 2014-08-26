# -*- coding: utf-8 -*-
from toolz import countby, pipe
from toolz.curried import drop, map

from .stages import read_vcf, match_variants
from .._compat import split


def pipeline(vcf_stream_ref, vcf_stream_alt):
  """Count identical/distinct genotypes between two VCF files.

  Returns:
    dict: counts for ``True`` matches and ``False`` non-matches.
  """
  complete, incomplete = read_vcf(vcf_stream_ref), read_vcf(vcf_stream_alt)

  genotype_sets = pipe(
    match_variants(complete, incomplete),  # matchup RS numbers
    map(drop(3)),                          # keep GT * 2
    map(map(split(sep='/'))),              # "0/0" -> ["0", "0"]
    map(map(set)),                         # convert both sides to sets
    map(list)                              # resolve inner ``map``s
  )

  # tally up overall results (reduce)
  return countby(lambda alleles: alleles[0] == alleles[1], genotype_sets)
