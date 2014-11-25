# -*- coding: utf-8 -*-
from __future__ import absolute_import
from itertools import tee

from toolz import concat, concatv, pipe
from toolz.curried import map, pluck

from .stages import export_excel_sheet, transpose
from .utils import encode_genotype, rsnumber_converter, vcf_headers


def pipeline(excel_path, base_vcf_stream):
  # export last sheet
  (excel_sheet_copy,
   excel_sheet) = tee(export_excel_sheet(excel_path, sheet_id=-1))

  # figure our where SNP columns begin
  snp_start = next(index for index, column in
                   enumerate(next(excel_sheet_copy))
                   if column.startswith('rs'))

  # pick out valid sample rows
  sample_rows = (row for row in excel_sheet
                 if row[1].startswith('ID')  # sample rows
                 or row[1] == 'SAMPLE')      # header row

  transposed_rows = pipe(
    sample_rows,
    pluck([slice(1,2), slice(snp_start, None)]),
    map(concat),
    transpose
  )

  for header_line in vcf_headers(samples=next(transposed_rows)):
    yield header_line

  # initialize RS number converter
  converter = rsnumber_converter(base_vcf_stream)

  for variant in transposed_rows:
    rs_number = variant[0]
    genotypes = variant[1:]

    # get base variant data based on RS number
    base = converter(rs_number)
    reference_allele = base[3]
    alternative_allele = base[4]

    # extract each base call for each genotype
    listed_genotypes = (genotype.split(' ') for genotype in genotypes)

    # encode genotypes as 1 / 0 instead of actual base (ACTG)
    encoded_genotypes = (
      encode_genotype(reference_allele, alternative_allele, genotype)
      for genotype in listed_genotypes
    )

    # stringify genotypes
    str_genotypes = ('/'.join(genotype) for genotype in encoded_genotypes)

    # join variant base, GT field, and stringified genotypes
    yield '\t'.join(concatv(base, ['GT'], str_genotypes))
