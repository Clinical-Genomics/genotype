# -*- coding: utf-8 -*-
import csv

from toolz import concatv, curry, pipe, partial
from toolz.curried import map, pluck

from .._compat import filterfalse


@curry
def startswith(prefix, string):
  """Match prefix pattern in the beginning of a string."""
  return string.startswith(prefix)


def _minimize_gt(gt_call):
  return gt_call.split(':')[0]


@curry
def _apply_to_last(function, sequence):
  return concatv(sequence[:-1], [function(sequence[-1])])


def read_vcf(vcf_stream):
  return pipe(
    vcf_stream,
    partial(filterfalse, startswith('#')),  # skip header/comment rows
    partial(csv.reader, delimiter='\t'),    # producer
    pluck([2, 3, 4, 9]),                    # extract: RS, REF, ALT, GT
    map(_apply_to_last(_minimize_gt)),      # 0/1:38... -> 0/1
    map(list)
  )


def match_variants(complete_stream, incomplete_stream, default='0/0'):
  """Expects sorted input.

  With default we can fill in a default case if a RS number is only
  found in the complete stream. Some pipelines e.g. don't report
  "variants" that are REF/REF (or 0/0).
  """
  # initializer
  incomplete_variant = next(incomplete_stream, None)

  # loop over complete stream
  for complete_variant in complete_stream:

    # check if current combo matches (rsnumber)
    if incomplete_variant and (incomplete_variant[0] == complete_variant[0]):

      # yield matching combo
      yield concatv(complete_variant, incomplete_variant[-1:])

      # re-initialize
      incomplete_variant = next(incomplete_stream, None)

    else:
      # yield one-sided combo and skip re-initialization
      # assume we didn't find the variant because of ``default`` case
      yield concatv(complete_variant, [default])



