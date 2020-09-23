"""Tests for the delete CLI function"""

import logging

from alchy import Manager
from click.testing import CliRunner

from genotype.cli.match_cmd import check_cmd
from genotype.store.models import Analysis, Sample


def test_match_no_args(cli_runner: CliRunner, sequence_db: Manager):
    # GIVEN a database with a sample loaded (one analysis)

    # WHEN running check without any samples
    result = cli_runner.invoke(check_cmd, [], obj={"db": sequence_db})

    # THEN the cli should exit non zero
    assert result.exit_code != 0


def test_match_one_ind(cli_runner: CliRunner, sequence_db: Manager, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with a sample loaded (one analysis)
    assert Analysis.query.count() == 1
    assert Sample.query.count() == 1
    sample_id = Sample.query.first().id

    # WHEN running match with one sample
    result = cli_runner.invoke(check_cmd, [sample_id], obj={"db": sequence_db})

    # THEN the cli should exit zero
    assert result.exit_code == 0
    # THEN it should be communicated that no genotyping exist
    assert "no genotyping analysis loaded" in caplog.text
