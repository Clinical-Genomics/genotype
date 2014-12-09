# -*- coding: utf-8 -*-
from toolz import curry, get


@curry
def match_field(id_map, row, field=0):
  """Datastructure to match (cheaply) against."""
  # match against the identifier map
  # if the field index is "out of range", ``False`` is returned as well
  return get(field, row, default='__return_false__') in id_map
