# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from click.testing import CliRunner

from taboo.subcommands import split


def test_split():
  runner = CliRunner()
  result = runner.invoke(split)
  assert result.exit_code == 2  # missing vcf_stream
