# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from taboo._compat import split


def test_split():
  name_parts = split('Paul Thomas Anderson', sep=' ')
  assert name_parts == ['Paul', 'Thomas', 'Anderson']

  # test default separator is tab
  parts = split('#CHROM\tPOS\tRSNUMBER')
  assert parts == ['#CHROM', 'POS', 'RSNUMBER']

  # test empty string
  assert split('') == ['']
