# -*- coding: utf-8 -*-
from genotype.store.models import Sample, SNP


def test_init(invoke_cli, existing_db, snp_path, snp_sequence):
    # GIVEN an empty exising database
    snp_count = len(snp_sequence)
    db_uri = existing_db.engine.url
    assert Sample.query.count() == 0
    assert SNP.query.count() == 0
    # WHEN running 'init' subcommand in CLI
    result = invoke_cli(['-d', db_uri, 'init', snp_path])
    # THEN it should work and populate the database with SNPs
    assert result.exit_code == 0
    assert SNP.query.count() == snp_count

    # GIVEN a database which is already set up
    assert SNP.query.count() == snp_count
    # WHEN running 'init' subcommand again
    result = invoke_cli(['-d', db_uri, 'init', snp_path])
    # THEN it should abort and log a warning
    assert result.exit_code != 0
    assert 'WARNING' in result.output

    # GIVEN a database which is already set up
    assert SNP.query.count() == snp_count
    # WHEN running 'init' subcommand again **with reset flag**
    result = invoke_cli(['-d', db_uri, 'init', '--reset', snp_path])
    # THEN it should tear down the db first and work!
    assert result.exit_code == 0
    assert SNP.query.count() == snp_count
