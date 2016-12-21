# -*- coding: utf-8 -*-
from genotype.store.models import Sample


def test_add_many(genotype_db):
    # GIVEN multiple new samples
    new_samples = [Sample(id='ADM12'), Sample(id='ADM13')]
    # WHEN added to the session
    genotype_db.add_commit(*new_samples)
    # THEN all samples should be added
    assert Sample.query.all() == new_samples
