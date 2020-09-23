"""Unit tests for store API"""

from alchy import Manager

from genotype.store.models import Sample


def test_add_many(snp_db: Manager):
    # GIVEN multiple new samples
    new_samples = [Sample(id="ADM12"), Sample(id="ADM13")]
    # WHEN added to the session
    snp_db.add_commit(*new_samples)
    # THEN all samples should be added
    assert Sample.query.all() == new_samples
