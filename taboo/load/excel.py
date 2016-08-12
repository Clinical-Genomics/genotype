# -*- coding: utf-8 -*-
import os
import logging

import xlrd

from taboo.compat import zip
from taboo.exc import SexConflictError
from taboo.store.models import Analysis, Genotype

log = logging.getLogger(__name__)


def load_excel(file_path, file_contents, include_key=None):
    """Load genotypes from an Excel file.

    3. go over SNPs, build genotypes and link to analyses
    4. return analyses

    Args:
        excel_file (path): path to to Excel file

    Returns:
        List[Analysis]: list of Analysis records
    """
    # import Excel (book) file
    book = xlrd.open_workbook(file_contents=file_contents)
    sheet = find_sheet(book, sheet_id=-1)
    # create new Sample records
    sample_ids = parse_sampleids(sheet, include_key=include_key)
    # create new Analyses records
    source = os.path.abspath(file_path)
    analyses = [Analysis(type='genotype', source=source, sample_id=sample_id)
                for sample_id in sample_ids]

    # figure our where SNP columns begin
    header_row = sheet.row_values(0)
    snp_start = find_column(header_row, pattern='rs')
    rsnumber_columns = header_row[snp_start:]
    # find out the start of sex prediction columns
    sex_start = find_column(header_row, pattern='ZF_')
    sex_cols = slice(sex_start, sex_start + 3)

    # parse rows that match the "include key"
    rows = (sheet.row_values(rowx) for rowx in range(1, sheet.nrows))
    if include_key:
        rows = (row for row in rows if include_key in row[1])

    for new_analysis, row in zip(analyses, rows):
        predicted_sex = parse_sex(row[sex_cols])
        new_genotypes = build_genotypes(rsnumber_columns, row[snp_start:])
        for genotype in new_genotypes:
            new_analysis.genotypes.append(genotype)
        new_analysis.sex = predicted_sex
        yield new_analysis


def parse_sampleids(sheet, include_key=None):
    """Build samples from Excel sheet."""
    sample_ids = (cell.value for cell in sheet.col_slice(1, 1))
    if include_key:
        sample_ids = (sample_id.split('-')[-1] for sample_id
                      in sample_ids if include_key in sample_id)
    return sample_ids


def build_genotypes(rsnumbers, row_values):
    """Build genotypes from an Excel row."""
    for rsnumber, genotype_str in zip(rsnumbers, row_values):
        alleles = genotype_str.split()
        new_genotype = Genotype(rsnumber=rsnumber, allele_1=alleles[0],
                                allele_2=alleles[1])
        yield new_genotype


def parse_sex(sex_cells):
    """Parse the sex prediction from a sample row."""
    predictions = set()

    # first marker
    if sex_cells[0] == 'T C':
        predictions.add('male')
    elif sex_cells[0] == 'C C':
        predictions.add('female')

    # second marker
    if sex_cells[1] == 'T C':
        predictions.add('male')
    elif sex_cells[1] == 'C C':
        predictions.add('female')

    # third marker
    if sex_cells[2] == 'C T':
        predictions.add('male')
    elif sex_cells[2] == 'T T':
        predictions.add('female')

    if len(predictions) == 1:
        return predictions.pop()
    elif len(predictions) == 0:
        # all assays failed
        return 'unknown'
    elif len(predictions) == 2:
        # assays returned conflicting results
        message = "conflicting sex predictions: {}".format(sex_cells)
        raise SexConflictError(message)


def find_sheet(book, sheet_id=0):
    """Find a sheet in an Excel book.

    Args:
        book (xlrd.book.Book): initialized Excel book object
        sheet_id (int or str): index or name of sheet to export

    Yields:
        xlrd.sheet.Sheet: individual Excel sheet
    """
    # extract sheet by index or name
    if isinstance(sheet_id, int):
        return book.sheet_by_index(sheet_id)
    elif isinstance(sheet_id, str):
        return book.sheet_by_name(sheet_id)


def find_column(header_row, pattern='rs'):
    """Find the first column in a row that matches a pattern."""
    snp_columns = (index for index, column in enumerate(header_row)
                   if column.startswith(pattern))

    # return the first index
    return next(snp_columns)
