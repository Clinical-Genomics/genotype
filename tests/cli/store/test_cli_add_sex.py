"""Tests for updating sex in the database"""

import logging

from alchy import Manager
from click.testing import CliRunner

from genotype.cli.store_cmd import add_sex
from genotype.store.models import Analysis, Sample


def test_add_sex(cli_runner: CliRunner, sequence_ctx: dict):
    """Test to update sex for a sample with the CLI"""
    # GIVEN an existing database with a sample without sex
    sample_obj = Sample.query.first()
    assert sample_obj.sex is None
    sample_id = sample_obj.id

    # WHEN adding information about the sex of the sample with the CLI
    sex = "female"
    result = cli_runner.invoke(add_sex, [sample_id, "-s", sex], obj=sequence_ctx)

    # THEN the command should exit successfully
    assert result.exit_code == 0
    # THEN the sample should have a sex
    assert Sample.query.get(sample_id).sex == sex


def test_add_sex_non_existing_sample(cli_runner: CliRunner, sequence_ctx: dict):
    """Try to update the sex for a non existing sample"""
    # GIVEN a database with a sample without a gender
    # GIVEN the id to a non existing sample
    sample_id = "idontexist"
    assert Sample.query.get(sample_id) is None

    # WHEN trying to add information about a non-existing sample
    sex = "female"
    result = cli_runner.invoke(add_sex, ["idontexist", "-s", sex], obj=sequence_ctx)

    # THEN it the CLI should exit with a non zero exit code
    assert result.exit_code != 0


def test_add_sex_analysis(cli_runner: CliRunner, sequence_ctx: dict):
    # GIVEN an existing database with sample + analysis
    sample_obj = Sample.query.first()
    sample_id = sample_obj.id
    analysis_obj = Analysis.query.first()
    analysis_type = analysis_obj.type
    # GIVEN that the analysis has no sex
    assert analysis_obj.sex is None

    sex = "male"
    # WHEN updating the analysis sex determination
    result = cli_runner.invoke(add_sex, [sample_id, "-a", analysis_type, sex], obj=sequence_ctx)

    # THEN the CLI should be OK and the analysis sex should be updated
    assert result.exit_code == 0
    assert Analysis.query.first().sex == sex


def test_add_sex_non_existing_analysis(cli_runner: CliRunner, sequence_ctx: dict, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN an existing database with sample + analysis
    sample_id = Sample.query.first().id
    analysis_type = "genotype"
    # GIVEN that an analysis that does not exist
    assert Analysis.query.filter_by(sample_id=sample_id, type=analysis_type).first() is None

    sex = "male"
    # WHEN updating the analysis sex determination
    result = cli_runner.invoke(add_sex, [sample_id, "-a", analysis_type, sex], obj=sequence_ctx)

    # THEN the CLI should be OK
    assert result.exit_code == 0
    # THEN assert it was communicated that the analysis did not exist
    assert f"analysis not found: {sample_id}-{analysis_type}" in caplog.text
