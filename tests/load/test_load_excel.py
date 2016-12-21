# -*- coding: utf-8 -*-
import pytest
import xlrd

from genotype.exc import SexConflictError
from genotype.load import excel


def test_parse_sex():
    # GIVEN SNP cells matching 'female'
    sex_cells = ['C C', 'C C', 'T T']
    # WHEN parsing out the sex
    sex = excel.parse_sex(sex_cells)
    # THEN it should return 'female'
    assert sex == 'female'

    # GIVEN SNP cells matching 'male'
    sex_cells = ['T C', 'T C', 'C T']
    # WHEN parsing out the sex
    sex = excel.parse_sex(sex_cells)
    # THEN it should return 'male'
    assert sex == 'male'

    # GIVEN SNP cells with failed genotyping
    sex_cells = ['0 0', '0 0', '0 0']
    # WHEN parsing out the sex
    sex = excel.parse_sex(sex_cells)
    # THEN it should return 'unknown'
    assert sex == 'unknown'

    # GIVEN SNP cells with ambigous calls
    sex_cells = ['C C', 'T C', '0 0']
    # WHEN parsing out the sex
    # THEN it should raise an error
    with pytest.raises(SexConflictError):
        excel.parse_sex(sex_cells)


def test_find_sheet(excel_path):
    # GIVEN an Excel book with a sheet
    book = xlrd.open_workbook(excel_path)
    sheet_id = 'Sheet1'
    # WHEN finding a sheet by name (str)
    sheet = excel.find_sheet(book, sheet_id=sheet_id)
    # THEN it should return the correct sheet
    assert sheet.name == sheet_id
