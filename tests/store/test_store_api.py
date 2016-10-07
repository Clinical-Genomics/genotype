# -*- coding: utf-8 -*-
from taboo.store.models import Sample


def test_add_many(taboo_db):
    # GIVEN multiple new samples
    new_samples = [Sample(id='ADM12'), Sample(id='ADM13')]
    # WHEN added to the session
    taboo_db.add_commit(*new_samples)
    # THEN all samples should be added
    assert Sample.query.all() == new_samples
