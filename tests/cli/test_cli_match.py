"""Tests for the delete CLI function"""

import logging

from alchy import Manager
from click.testing import CliRunner

from genotype.cli.match_cmd import match_cmd
from genotype.store.models import Analysis, Sample


def test_match_no_args(cli_runner: CliRunner, sequence_db: Manager, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with a sample loaded (one analysis)

    # WHEN running match without any samples
    result = cli_runner.invoke(match_cmd, [], obj={"db": sequence_db})

    # THEN the cli should exit non zero
    assert result.exit_code != 0
    # THEN assert the correct information is communicated
    assert "you must supply at least one sample id" in caplog.text


def test_match_one_ind(cli_runner: CliRunner, sequence_db: Manager, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a database with a sample loaded (one analysis)
    assert Analysis.query.count() == 1
    assert Sample.query.count() == 1
    sample_id = Sample.query.first().id

    # WHEN running match without any samples
    result = cli_runner.invoke(match_cmd, [sample_id, "-a", "sequence"], obj={"db": sequence_db})

    # THEN the cli should exit non zero
    assert result.exit_code == 0
