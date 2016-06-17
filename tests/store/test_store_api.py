# -*- coding: utf-8 -*-
import pytest

from taboo.store.models import Sample


def test_add_many(taboo_db):
    # GIVEN multiple new samples
    new_samples = [Sample(id='ADM12'), Sample(id='ADM13')]
    # WHEN added to the session
    taboo_db.add(new_samples)
    taboo_db.save()
    # THEN all samples should be added
    assert Sample.query.all() == new_samples

    # GIVEN an unknown type to add, e.g. dict
    data = {'sample': Sample(id='ADM13')}
    # WHEN adding to session
    # THEN it should raise ValueError
    with pytest.raises(ValueError):
        taboo_db.add(data)
