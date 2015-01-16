# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from toolz import map

from taboo._compat import split
from taboo.utils import namebase, track_rows, startswith


def test_track_rows():
  lines = ['#header\trow\there', '#another\theader', 'lost\tdata', 'data!']
  rows = map(split(sep='\t'), lines)
  headers = list(track_rows(rows, start='#'))

  assert headers == lines[:2]
  assert next(rows) == [lines[3]]
