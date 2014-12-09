# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from codecs import open

from taboo.subcommands.vcfify import rsnumber_converter


class TestConfig:
  def setup(self):
    with open('tests/fixtures/rsnumber-converter.vcf', 'r') as handle:
      self.converter = rsnumber_converter(handle)

    self.base_variant = ['5', '89820984', 'rs10069050', 'T', 'C'] + 3*['.']
    self.gt_calls = ('C/C', 'C/A', 'C/A', 'C/C')

  def test_rsnumber_converter(self):
    # test simple case
    variant = ['19', '58928302', 'rs10423138', 'T', 'C', '.', '.', '.']
    assert variant == self.converter('rs10423138')

    # test fake rsnumber with custom default return value
    assert self.converter('Why me?', 'Because.') == 'Because.'
