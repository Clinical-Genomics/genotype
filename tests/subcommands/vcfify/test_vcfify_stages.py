# -*- coding: utf-8 -*-
from __future__ import absolute_import
from taboo.subcommands.vcfify import transpose, export_excel_sheet


class TestVcfifyStages:
  def setup(self):
    self.sample_rows = [['FAMILY', 'SAMPLE', 'RS1', 'RS2'],
                        ['Anderson', 'Bob', 'A T', 'G C'],
                        ['Brick', 'Oscar', 'A A', 'C A']]

    self.sample_transposed = [['FAMILY', 'Anderson', 'Brick'],
                              ['SAMPLE', 'Bob', 'Oscar'],
                              ['RS1', 'A T', 'A A'],
                              ['RS2', 'G C', 'C A']]

    self.sample_sliced = [['SAMPLE', 'RS2'],
                          ['Bob', 'G C'],
                          ['Oscar', 'C A']]

  def test_transpose(self):
    # Test with case above
    assert list(transpose(self.sample_rows)) == self.sample_transposed


def test_export_excel_sheet():
  # Open Excel file with only one sheet
  rows = list(export_excel_sheet('tests/fixtures/simple.xlsx'))
  assert len(rows) == 4
  assert rows[0][0] == 'FAMILY'
  assert len(rows[1]) == 12

  # Open Excel file with multiple sheets
  rows = list(export_excel_sheet('tests/fixtures/multi.xlsx', sheet_id=1))
  assert len(rows) == 5
  assert len(rows[2]) == 9

  # Select sheet with negative index
  rows = list(export_excel_sheet('tests/fixtures/multi.xlsx', sheet_id=-3))
  assert len(rows) == 4
  assert len(rows[2]) == 12

  # Select sheet by name
  rows = list(
    export_excel_sheet('tests/fixtures/multi.xlsx',
                        sheet_id='Sheet3')
  )
  assert len(rows) == 9
  assert len(rows[2]) == 13
