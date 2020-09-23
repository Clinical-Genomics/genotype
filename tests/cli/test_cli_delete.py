"""Tests for the delete CLI function"""

import logging

from alchy import Manager
from click.testing import CliRunner

from genotype.cli.delete_cmd import delete_cmd
from genotype.store.models import Analysis, Sample


def test_delete_analysis(cli_runner: CliRunner, sequence_ctx: dict):
    # GIVEN a database with a sample loaded (one analysis)
    assert Sample.query.count() == 1
    assert Analysis.query.count() == 1
    sample_id = Sample.query.first().id
    a_type = Analysis.query.first().type

    # WHEN deleting the analysis from the command line
    result = cli_runner.invoke(delete_cmd, ["-a", a_type, sample_id], obj=sequence_ctx)

    # THEN it should delete the analysis and leave the sample
    assert result.exit_code == 0
    assert Analysis.query.count() == 0
    assert Sample.query.count() == 1


def test_delete_non_existing_analysis(cli_runner: CliRunner, sequence_ctx: dict, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a non-existing analysis
    analysis_type = "genotype"
    sample_id = "sample"
    assert Analysis.query.filter_by(sample_id=sample_id, type=analysis_type).first() is None

    # WHEN deleting it
    result = cli_runner.invoke(delete_cmd, ["-a", analysis_type, sample_id], obj=sequence_ctx)

    # THEN it should abort the script
    assert result.exit_code != 0
    assert "analysis not loaded in database" in caplog.text


def test_delete_existing_sample(cli_runner: CliRunner, sequence_ctx: dict, sample_id: str, caplog):
    # GIVEN database with one sample
    assert Sample.query.count() == 1

    # WHEN deleting the whole sample
    result = cli_runner.invoke(delete_cmd, [sample_id], obj=sequence_ctx)

    # THEN the sample should disappear
    assert result.exit_code == 0
    assert Sample.query.count() == 0


def test_delete_non_existing_sample(cli_runner: CliRunner, sequence_ctx: dict, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a non-existing sample id
    sample_id = "i_dont_exist"
    assert Sample.query.get(sample_id) is None

    # WHEN deleting the sample
    result = cli_runner.invoke(delete_cmd, [sample_id], obj=sequence_ctx)

    # THEN it the cli should be aborted
    assert result.exit_code != 0
    # THEN assert it was communicated that the sample does not exist
    assert "sample not loaded in database" in caplog.text
