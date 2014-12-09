# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from click.testing import CliRunner

from taboo.cli import cli


def test_cli():
  runner = CliRunner()
  result = runner.invoke(cli, ['--version'])
  assert result.exit_code == 0
  assert 'version' in result.output
