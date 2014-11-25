# -*- coding: utf-8 -*-
from toolz import curry, map
import xlrd

from ..._compat import range, zip


@curry
def export_excel_sheet(book_path, sheet_id=0):
  """Export data from a sheet in an Excel book.

  Args:
    book_path (str): path to Excel book file
    sheet_id (int or str): index or name of sheet to export

  Yields:
    list: values from row in Excel sheet
  """
  # import excel (book) file
  xl = xlrd.open_workbook(book_path)

  # extract sheet by index or name
  if isinstance(sheet_id, int):
    sheet = xl.sheet_by_index(sheet_id)

  elif isinstance(sheet_id, str):
    sheet = xl.sheet_by_name(sheet_id)

  # yield each row, loop over all row indices
  for rowx in range(sheet.nrows):
    # access row by its row index
    yield sheet.row_values(rowx)


def transpose(a_list):
  """Transpose values in a 2D list (matrix).

  Args:
    a_list (list of list): 2D list

  Yields:
    list: row in transposed list
  """
  return map(list, zip(*a_list))
