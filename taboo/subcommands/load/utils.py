# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from toolz import map

from ..._compat import split, text_type
from ...utils import track_rows


def parse_compare(stream):
  stripped = map(text_type.rstrip, stream)
  rows = map(split(sep='\t'), stripped)
  # discard header rows
  headers = list(track_rows(rows, start='#'))[0][1:].split('\t')

  # columns are not fixed in terms of order
  gt_index = headers.index('gt-type')
  quality_index = headers.index('quality')
  concordance_index = headers.index('concordance')
  identity_index = headers.index('identity')
  samples_index = headers.index('samples')

  for row in rows:

    gt_types = row[gt_index].split(',')
    qualities = row[quality_index].split(',')
    qualities_int = [None if quality == 'unknown' else int(quality)
                     for quality in qualities]
    sample_ids = row[samples_index].split(',')

    yield dict(
      rs_number=row[identity_index],
      concordance=row[concordance_index],
      original_id=sample_ids[0],
      compared_id=sample_ids[1],
      original_genotype=gt_types[0],
      compared_genotype=gt_types[1],
      original_quality=qualities_int[0],
      compared_quality=qualities_int[1]
    )
