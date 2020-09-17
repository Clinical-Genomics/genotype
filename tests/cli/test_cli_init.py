"""Test the cli init cmds"""
import logging
from pathlib import Path

from click.testing import CliRunner

from genotype.cli.base_cmd import root
from genotype.cli.init_cmd import init_cmd


def test_root(cli_runner: CliRunner):
    # GIVEN the root command

    # WHEN executing the root command alone
    result = cli_runner.invoke(root)

    # THEN it should execute normally and print version string
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


def test_missing_command(cli_runner: CliRunner):
    # GIVEN a missing subcommand
    command = "i_dont_exist"

    # WHEN calling the CLI with the missing subcommand
    result = cli_runner.invoke(root, [command])

    # THEN the CLI should error and exit
    assert result.exit_code != 0


def test_with_config(cli_runner: CliRunner, config_path: Path):
    # GIVEN a config file

    # WHEN running the CLI with the config
    result = cli_runner.invoke(root, ["--config", str(config_path), "add-sex", "--help"])

    # THEN is should work :P
    assert result.exit_code == 0


def test_init_db_cli(cli_runner: CliRunner, config_path: Path, snp_path: Path, caplog):
    caplog.set_level(logging.DEBUG)
    # GIVEN a config file and path to snp file

    # WHEN running the CLI with the config
    result = cli_runner.invoke(root, ["--config", str(config_path), "init", str(snp_path)])

    # THEN is should work :P
    assert result.exit_code == 0
    # THEN assert that it was successfully created
    assert "Database successfully setup" in caplog.text
