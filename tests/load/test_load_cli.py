# -*- coding: utf-8 -*-
from genotype.store.models import Analysis, SNP, Sample


def test_load_bcf(invoke_cli, bcf_path, setexist_db):
    # GIVEN a database with some SNPs loaded and one sample
    sample_id = '000139T'
    db_uri = setexist_db.engine.url
    assert SNP.query.count() > 0
    assert Sample.query.count() == 1
    assert Analysis.query.count() == 1
    # WHEN loading a BCF from the command line (single sample)
    result = invoke_cli(['-d', db_uri, 'load', bcf_path])
    # THEN it works and loads a sample with an analysis
    assert result.exit_code == 0
    assert Sample.query.count() == 2
    assert Analysis.query.count() == 2
    new_analysis = Analysis.query.filter_by(type='sequence').first()
    assert Sample.query.get(sample_id).analyses[0] == new_analysis

    # GIVEN the database is already loaded with the analysis
    # see above
    # WHEN loading the same resource again (same sample id)
    result = invoke_cli(['-d', db_uri, 'load', bcf_path])
    # THEN it should exit succesfully but log a warning
    assert result.exit_code == 0
    assert 'WARNING' in result.output


def test_load_excel(invoke_cli, excel_path, setexist_db):
    # GIVEN a database with some SNPs loaded
    db_uri = setexist_db.engine.url
    assert SNP.query.count() > 0
    # WHEN loading an Excel book from the command line (multi-sample)
    result = invoke_cli(['-d', db_uri, 'load', excel_path, '-k', 'ID-CG-'])
    # THEN it works and loads a sample with an analysis
    assert result.exit_code == 0
    assert Sample.query.count() > 0
    assert Analysis.query.count() == Sample.query.count()


def test_delete(invoke_cli, setexist_db):
    # GIVEN a database with a sample loaded (one analysis)
    db_uri = setexist_db.engine.url
    assert Sample.query.count() == 1
    assert Analysis.query.count() == 1
    sample_id = Sample.query.first().id
    a_type = Analysis.query.first().type
    # WHEN deleting the analysis from the command line
    result = invoke_cli(['-d', db_uri, 'delete', '-a', a_type, sample_id])
    # THEN it should delete the analysis and leave the sample
    assert result.exit_code == 0
    assert Analysis.query.count() == 0
    assert Sample.query.count() == 1

    # GIVEN a non-existing analysis
    a_type = 'sequence'
    # WHEN deleting it
    result = invoke_cli(['-d', db_uri, 'delete', '-a', a_type, sample_id])
    # THEN it should abort the script
    assert result.exit_code != 0
    assert Sample.query.count() == 1

    # GIVEN database with one sample
    # see above
    # WHEN deleting the whole sample
    result = invoke_cli(['-d', db_uri, 'delete', sample_id])
    # THEN the sample should dissapear
    assert result.exit_code == 0
    assert Sample.query.count() == 0

    # GIVEN a non-existing sample id
    sample_id = 'iDontExist'
    # WHEN deleting the sample
    result = invoke_cli(['-d', db_uri, 'delete', sample_id])
    # THEN it the CLI should be aborted
    assert result.exit_code != 0
