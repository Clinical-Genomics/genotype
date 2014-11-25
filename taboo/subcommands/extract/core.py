# -*- coding: utf-8 -*-
import csv
from itertools import tee

from toolz import pipe
from toolz.curried import filter, map

from .stages import match_field
from ...utils import track_rows


def pipeline(vcf_stream, rsnumbers_stream):
  # read in rsnumbers
  rsnumbers = set([rsnumber.strip() for rsnumber in rsnumbers_stream])

  # yield all header rows
  vcf_reader, vcf_reader_copy = tee(csv.reader(vcf_stream, delimiter='\t'))

  # keep header/comment lines intact
  for comment_line in track_rows(vcf_reader_copy):
    yield comment_line

  vcf_lines = pipe(
    vcf_reader,
    filter(match_field(rsnumbers, field=2)),
    map('\t'.join)
  )

  for vcf_line in vcf_lines:
    yield vcf_line
