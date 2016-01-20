# -*- coding: utf-8 -*-
import os
import logging

from sqlalchemy.exc import IntegrityError
import xlrd

from taboo.compat import zip
from taboo.store.models import Genotype

logger = logging.getLogger(__name__)


def csvify(sheet):
    """Convert an Excel sheet into CSV output.

    Args:
        sheet (xlrd.sheet.Sheet): individual sheet object

    Yields:
        list: values from row in sheet
    """
    # yield each row, loop over all row indices
    for rowx in range(sheet.nrows):
        # access row by its row index
        yield sheet.row_values(rowx)


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


def extract(row, snp_start, sex_start):
    """Extract relevant data from Excel rows.

    Args:
        row (list): list of values from row in genotype sheet

    Returns:
        dict: with `sample_id` and `genotypes`
    """
    # remove leading 'IDX-CG-'
    sample_id = row[1].split('-')[-1]
    genotype_columns = row[snp_start:]
    sex_columns = row[sex_start:sex_start+3]
    return {
        'sample_id': sample_id,
        'genotypes': genotype_columns,
        'sex': sex_columns
    }


def parse_sex(markers):
    """Parse the sex prediction from a sample row."""
    predictions = set()

    # first marker
    if markers[0] == 'T C':
        predictions.add('male')
    elif markers[0] == 'C C':
        predictions.add('female')

    # second marker
    if markers[1] == 'T C':
        predictions.add('male')
    elif markers[1] == 'C C':
        predictions.add('female')

    # third marker
    if markers[2] == 'C T':
        predictions.add('male')
    elif markers[2] == 'T T':
        predictions.add('female')

    if len(predictions) == 1:
        return predictions.pop()
    elif len(predictions) == 0:
        # all assays failed
        return 'unknown'
    elif len(predictions) == 2:
        # assays returned conflicting results
        logger.warn("conflicting sex predictions: %s", markers)
        return 'conflict'


def load_excel(store, book_path, experiment='genotyping', source=None,
               force=False, include_key=None):
    """Load samples from a MAF Excel sheet with genotypes.

    Args:
        book_path (path): path to Excel book file
    """
    # import excel (book) file
    book = xlrd.open_workbook(book_path)
    sheet = find_sheet(book, sheet_id=-1)
    rows = csvify(sheet)

    # figure our where SNP columns begin
    header_row = next(rows)
    snp_start = find_column(header_row, pattern='rs')
    rsnumber_columns = header_row[snp_start:]

    # find out the start of sex prediction columns
    sex_start = find_column(header_row, pattern='ZF_')

    # parse rows that match the "include key"
    if include_key:
        rows = (row for row in rows if include_key in row[1])

    data_rows = (extract(row, snp_start, sex_start) for row in rows)
    source_id = source or os.path.abspath(book_path)
    parsed_rows = ((row['sample_id'],
                    zip(rsnumber_columns, row['genotypes']),
                    row['sex'])
                   for row in data_rows)

    sample_ids = []
    analyses = []
    for sample_id, genotypes, sex_columns in parsed_rows:
        sample_ids.append(sample_id)
        analyses.append({
            'sex': parse_sex(sex_columns),
            'sample_id': sample_id,
            'genotypes': [{
                'rsnumber': rsnumber,
                'allele_1': genotype_str.split()[0],
                'allele_2': genotype_str.split()[1]
            } for rsnumber, genotype_str in genotypes]
        })

    samples = {sample_id: store.get_or_create('sample', sample_id=sample_id)
               for sample_id in sample_ids}

    for analysis in analyses:
        sample_obj = samples[analysis['sample_id']]
        sample_id = sample_obj.sample_id
        analysis_exists = store.analysis(sample_id, experiment, check=True)

        if analysis_exists:
            logger.warn("analysis already added: %s", sample_id)
            if force:
                logger.info('removing existing analysis')
                store.remove(sample_id, experiment)

        if (not analysis_exists) or force:
            analysis_obj = store.add_analysis(sample_obj, experiment,
                                              source_id, analysis['sex'])
            new_genotypes = [Genotype(**gt) for gt in analysis['genotypes']]
            analysis_obj.genotypes = new_genotypes

            store.add(analysis_obj)
            try:
                store.save()
            except IntegrityError as exception:
                store.session.rollback()
                logger.error('unknown exception, multiple alleles?')
                raise exception
            yield analysis_obj
