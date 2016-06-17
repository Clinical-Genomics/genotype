# -*- coding: utf-8 -*-


def test_root(invoke_cli):
    # GIVEN the root command
    # WHEN executing the root command alone
    result = invoke_cli()
    # THEN it should execute normally and print version string
    assert result.exit_code == 0
    assert result.output.startswith('Usage:')


def test_missing_command(invoke_cli):
    # GIVEN a missing subcommand
    command = 'idontexist'
    # WHEN calling the CLI with the missing subcommand
    result = invoke_cli([command])
    # THEN the CLI should error and exit
    assert result.exit_code != 0


def test_logging_to_file(tmpdir, invoke_cli):
    # GIVEN an empty directory
    assert tmpdir.listdir() == []
    # WHEN running the CLI to display some help for a subcommand
    log_path = tmpdir.join('stderr.log')
    result = invoke_cli(['--log-file', str(log_path), 'add-sex', '--help'])
    assert result.exit_code == 0
    assert tmpdir.listdir() == [log_path]


def test_with_config(invoke_cli, config_path):
    # GIVEN a config file
    # WHEN running the CLI with the config
    result = invoke_cli(['--config', config_path, 'add-sex', '--help'])
    # THEN is should work :P
    assert result.exit_code == 0
