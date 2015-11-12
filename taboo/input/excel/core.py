# -*- coding: utf-8 -*-
import logging

from sqlalchemy.exc import IntegrityError
import xlrd

from taboo._compat import zip
from taboo.store.models import Sample, Genotype

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


def rsnumber_start(header_row):
    """Figure out from which column the SNP information starts."""
    snp_columns = (index for index, column in enumerate(header_row)
                   if column.startswith('rs'))

    # return the first index
    return next(snp_columns)


def extract(row, snp_start):
    """Extract relevant data from Excel rows.

    Args:
        row (list): list of values from row in genotype sheet

    Returns:
        dict: with `sample_id` and `genotypes`
    """
    # remove leading 'IDX-'
    sample_id = row[1].split('-')[-1]
    genotype_columns = row[snp_start:]
    return {
        'sample_id': sample_id,
        'genotypes': genotype_columns
    }


def build_genotype(rsnumber, sample, allele_1, allele_2):
    """Build Genotype object without commiting parent Sample."""
    genotype = Genotype(rsnumber=rsnumber, allele_1=allele_1, allele_2=allele_2)
    genotype.sample = sample
    return genotype


def objectify(sample_id, experiment, source, genotypes):
    """Create ORM objects from parsed data."""
    new_sample = Sample(sample_id=sample_id, experiment=experiment,
                        source=source)
    new_genotypes = [build_genotype(rsnumber, sample, *genotype_str.split())
                     for rsnumber, genotype_str in rsnumber_genotypes]
    return {
        'sample': new_sample,
        'genotypes': new_genotypes


    }


def commit(store, sample, genotypes):
    """Commit everything belonging to a sample."""
    try:
        # commit samples and variants to get ids
        store.add(sample, *genotypes)
        store.save()
        return sample
    except IntegrityError as exception:
        store.session.rollback()
        logger.warn("conflict, skipping %s", sample.sample_id)
        return None


def load_excel(store, book_path, experiment='genotyping', source=None):
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
    snp_start = rsnumber_start(header_row)
    rsnumber_columns = header_row[snp_start:]

    data_rows = (extract(row, snp_start) for row in rows)
    source_id = source or book_path
    parsed_rows = ((row['sample_id'], zip(rsnumber_columns, row['genotypes']))
                   for row in data_rows)

    objects = (objectify(sample_id, experiment, source_id, genotypes)
               for sample_id, genotypes in parsed_rows)

    for data in objects:
        sample_obj = commit(data['sample'], data['genotypes'])
        if sample_obj:
            yield sample_obj
