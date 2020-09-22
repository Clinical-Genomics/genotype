"""Tests for the load mixins"""

from typing import List

from alchy import Manager

from genotype.store import api
from genotype.store.models import Analysis, Genotype, Sample


def test_add_analysis(genotype_db: Manager, sample_id: str, analysis_obj: Analysis):
    """Test to add an analysis to a empty database"""
    # GIVEN a new Analysis to be added to an empty database
    assert Analysis.query.first() is None
    assert Sample.query.first() is None

    # WHEN adding it to the database
    api.add_analysis(genotype_db, analysis_obj)

    # THEN it should work and add analysis, sample, and genotypes
    assert Sample.query.count() == 1
    assert Sample.query.first().id == sample_id
    assert Analysis.query.count() == 1
    assert Analysis.query.first().sample == Sample.query.first()
    assert Genotype.query.count() == 1
    assert Genotype.query.all() == Analysis.query.first().genotypes


def test_add_analysis_when_exist(
    analysis_db: Manager, new_genotypes: List[Genotype], sample_id: str
):
    """Test to add an analysis when analysis already exists"""
    # GIVEN an already loaded analysis and a new conflicting one
    assert Analysis.query.first() is not None

    # GIVEN a new analysis with the same sample
    new_analysis = Analysis(
        type="genotype", sample_id=sample_id, genotypes=new_genotypes, sex="female"
    )

    # WHEN trying to add it again (update)
    is_saved = api.add_analysis(analysis_db, new_analysis)

    # THEN it should return None since the analysis was not saved
    assert is_saved is None


def test_overwrite_existing_analysis(
    analysis_db: Manager, sample_id: str, new_genotypes: List[Genotype]
):
    # GIVEN a database with an analysis where sex is not specified
    assert Analysis.query.first().sex is None

    # GIVEN a new analysis with the same sample where sex is specified
    new_analysis = Analysis(
        type="genotype", sample_id=sample_id, genotypes=new_genotypes, sex="female"
    )

    # WHEN adding it with force flag
    api.add_analysis(analysis_db, new_analysis, replace=True)

    # THEN it should remove the old analysis before re-adding it
    assert Analysis.query.count() == 1
    assert Analysis.query.first().sex == "female"


def test_new_comment_is_added_when_replacing(genotype_db: Manager, sample_id: str):
    # GIVEN an old analysis with a comment and a new one
    sample_obj = Sample(id=sample_id, comment="a comment")
    genotype_db.add_commit(sample_obj)

    genotypes = [Genotype(rsnumber="rs12", allele_1="A", allele_2="T")]
    analysis = Analysis(type="genotype", sample_id=sample_id, genotypes=genotypes, sex="female")

    api.add_analysis(genotype_db, analysis)
    sample_obj = Sample.query.first()
    old_comment = sample_obj.comment
    assert old_comment is not None

    new_analysis = Analysis(type="genotype", sample_id=sample_id)

    # WHEN replacing the old with the new analysis
    api.add_analysis(genotype_db, new_analysis, replace=True)

    # THEN it should append a log message to the comment on the sample
    sample_obj = Sample.query.first()
    new_comment = sample_obj.comment
    assert old_comment in new_comment
    assert new_comment != old_comment
