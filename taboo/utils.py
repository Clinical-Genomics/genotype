# -*- coding: utf-8 -*-
"""
taboo.utils
~~~~~~~~~~~~

Various general functionality used (possibly) across the package.
"""
import os

from toolz import compose, curry, first


# __doc__ is read-only...
# Usage:
#   >>> namebase('/var/pass.txt')
#   'pass'
namebase = compose(first, os.path.splitext, os.path.basename)


def track_rows(rows, start='#'):
  """Move an iterator until lines don't start with a specific pattern.

  Works by introducing a ``break`` when the pattern no longer returns a
  match.

  Note that the first item that doesn't match the pattern is lost! Use
  something like ``itertools.tee`` if you need this value.

  Args:
    rows (iterable): iterator to loop through
    start (str, optional): pattern to match beginning of lines with

  Yields:
    str: joined line on tab-char with matching start pattern
  """
  for row in rows:
    if row[0].startswith(start):
      yield '\t'.join(row)
    else:
      break

@curry
def startswith(prefix, string):
  """Match prefix pattern in the beginning of a string."""
  return string.startswith(prefix)
