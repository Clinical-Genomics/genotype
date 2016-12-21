# -*- coding: utf-8 -*-
from genotype.store import api
from genotype.store.models import Analysis, Genotype, Sample


def test_add_analysis(sample_db):
    # GIVEN a new Analysis to be added to an empty database
    assert Analysis.query.first() is None
    sample_id = 'sample'
    genotypes = [Genotype(rsnumber='rs12', allele_1='A', allele_2='T')]
    new_analysis = Analysis(type='genotype', sample_id=sample_id,
                            genotypes=genotypes)
    # WHEN adding it to the database
    api.add_analysis(sample_db, new_analysis)
    # THEN it should work and add analysis, sample, and genotypes
    assert Sample.query.count() == 1
    assert Sample.query.first().id == sample_id
    assert Analysis.query.count() == 1
    assert Analysis.query.first().sample == Sample.query.first()
    assert Genotype.query.count() == 1
    assert Genotype.query.all() == Analysis.query.first().genotypes

    # GIVEN an already loaded analysis and a new conflicting one
    # see above...
    new_genotypes = [Genotype(rsnumber='rs12', allele_1='A', allele_2='T')]
    newer_analysis = Analysis(type='genotype', sample_id=sample_id,
                              genotypes=new_genotypes, sex='female')
    # WHEN trying to add it again (update)
    is_saved = api.add_analysis(sample_db, newer_analysis)
    # THEN it should return None
    assert is_saved is None

    # GIVEN an old analysis
    assert Analysis.query.first().sex is None
    # WHEN adding it with force flag
    api.add_analysis(sample_db, newer_analysis, replace=True)
    # THEN it should remove the old analysis before re-adding it
    assert Analysis.query.count() == 1
    assert Analysis.query.first().sex == 'female'

    # GIVEN an old analysis with a comment and a new one
    old_comment = Sample.query.first().comment
    assert old_comment is not None
    newest_analysis = Analysis(type='genotype', sample_id=sample_id)
    # WHEN replacing the old with the new analysis
    api.add_analysis(sample_db, newest_analysis, replace=True)
    # THEN it should append a log message to the comment on the sample
    new_comment = Sample.query.first().comment
    assert old_comment in new_comment
    assert new_comment != old_comment
