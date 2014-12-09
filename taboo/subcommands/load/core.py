# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .models import Comparison
from .store import Store
from .utils import parse_compare


def load_comparison(compare_stream, uri=':memory:', dialect='sqlite'):
  """Load new genotype comparison data into the store."""
  # connect to database
  store = Store(uri)
  store.set_up()

  for compare_data in parse_compare(compare_stream):
    comparison = Comparison(**compare_data)

    # add models to session
    store.add(comparison)

  # commit comparisons
  store.save()
