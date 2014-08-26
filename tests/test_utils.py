# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from taboo._compat import split
from taboo.utils import namebase, track_rows


def test_namebase():
  # test absolute path
  assert namebase('/var/pass.txt') == 'pass'

  # test filename with extension
  assert namebase('config.ini') == 'config'

  # test relative path
  assert namebase('folder/some_file.py') == 'some_file'

  # test "multiple" extensions
  assert namebase('alignment.bam.bai') == 'alignment.bam'


def test_track_rows():
  lines = ['#header\trow\there', '#another\theader', 'lost\tdata', 'data!']
  rows = map(split(sep='\t'), lines)
  headers = list(track_rows(rows, start='#'))

  assert headers == lines[:2]
  assert next(rows) == [lines[3]]
