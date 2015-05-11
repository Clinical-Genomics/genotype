# -*- coding: utf-8 -*-
from sqlalchemy.exc import IntegrityError
import xlrd

import taboo.store
import taboo._compat
from taboo.store.models import Sample, Genotype


def export_excel_sheet(book_path, sheet_id=0):
  """Export data from a sheet in an Excel book.

  Args:
    book_path (str): path to Excel book file
    sheet_id (int or str): index or name of sheet to export

  Yields:
    list: values from row in Excel sheet
  """
  # import excel (book) file
  excel_book = xlrd.open_workbook(book_path)

  # extract sheet by index or name
  if isinstance(sheet_id, int):
    sheet = excel_book.sheet_by_index(sheet_id)

  elif isinstance(sheet_id, str):
    sheet = excel_book.sheet_by_name(sheet_id)

  # yield each row, loop over all row indices
  for rowx in range(sheet.nrows):
    # access row by its row index
    yield sheet.row_values(rowx)


def rsnumber_start(header_row):
    """Figure out from which column the SNP information starts."""
    snp_columns = (index for index, column in enumerate(header_row)
                   if column.startswith('rs'))

    # return the first index
    return next(snp_columns)


def load_excel(store, excel_path, origin='genotyping'):
    """Convert MAF Excel sheet with genotypes to a VCF file."""
    # export last sheet
    excel_sheet = export_excel_sheet(excel_path, sheet_id=-1)

    # figure our where SNP columns begin
    header_row = next(excel_sheet)
    snp_start = rsnumber_start(header_row)
    rsnumber_columns = header_row[snp_start:]

    for sample_row in excel_sheet:
        sample_id = sample_row[1].split('-')[-1]  # remove leading 'IDX-'
        genotype_columns = sample_row[snp_start:]

        sample = Sample(sample_id=sample_id, origin=origin)

        rsnumber_genotypes = taboo._compat.zip(rsnumber_columns, genotype_columns)
        genotypes = [build_genotype(rsnumber, sample, *genotype_str.split())
                     for rsnumber, genotype_str in rsnumber_genotypes]

        try:
            # commit samples and variants to get ids
            store.add(sample, *genotypes)
            store.save()
        except IntegrityError as exception:
            store.session.rollback()
            raise exception


def build_genotype(rsnumber, sample, allele_1, allele_2):
    """Build Genotype object without commiting parent Sample."""
    genotype = Genotype(rsnumber=rsnumber, allele_1=allele_1, allele_2=allele_2)
    genotype.sample = sample

    return genotype
