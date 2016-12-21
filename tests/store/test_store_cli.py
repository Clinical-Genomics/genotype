# -*- coding: utf-8 -*-
from genotype.store.models import Analysis, Sample


def test_add_sex(invoke_cli, setexist_db):
    # GIVEN an existing database with a loaded sample
    db_uri = setexist_db.engine.url
    sample_id = 'ADM12'
    new_sample = Sample(id=sample_id)
    setexist_db.add_commit(new_sample)
    # WHEN adding information about the sex of the sample
    sex = 'female'
    result = invoke_cli(['-d', db_uri, 'add-sex', sample_id, '-s', sex])
    # THEN the database should update with the information
    assert result.exit_code == 0
    assert Sample.query.get(sample_id).sex == sex

    # WHEN trying to add information about non-existing sample
    result = invoke_cli(['-d', db_uri, 'add-sex', 'idontexist', '-s', sex])
    # THEN it should about the CLI
    assert result.exit_code != 0


def test_add_sex_analysis(invoke_cli, setexist_db):
    # GIVEN an existing database with sample + analysis
    db_uri = setexist_db.engine.url
    sex = 'male'
    sample_id = Sample.query.first().id
    analysis = Analysis.query.first()
    a_type = analysis.type
    assert analysis.sex != sex
    # WHEN updating the analysis sex determination
    result = invoke_cli(['-d', db_uri, 'add-sex', '-a', a_type, sex, sample_id])
    # THEN the CLI should be OK and the analysis sex should be updated
    assert result.exit_code == 0
    assert Analysis.query.first().sex == sex
