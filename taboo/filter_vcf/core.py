# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import csv
from itertools import tee
import re

from .._compat import filterfalse
from ..utils import startswith, track_rows


def pipeline(vcf_stream):
  # yield all header rows
  vcf_reader, vcf_reader_copy = tee(csv.reader(vcf_stream, delimiter='\t'))

  # keep VCF header lines
  for header_line in track_rows(vcf_reader_copy):
    yield header_line

  for row in filterfalse(lambda line: startswith('#', line[0]), vcf_reader):
    # keep the first 7 columns intact
    new_row = row[:7]

    # info column
    info = row[7]
    # extract 'DP' => approximate read depth
    new_row.append(re.search(';(DP=[0-9]*);', info).groups()[0])

    # some lines (variants) lack GT calls for some reason
    # but they still have read depth estimate etc.
    # because all samples are homozygous for the reference allele?
    if len(row) > 8:
      # GT call format
      new_row.append(row[8])

      # extract GT-calls columns
      new_row += row[9:]

    # combine the result we want to keep
    yield '\t'.join(new_row)
