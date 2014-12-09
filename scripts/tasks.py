#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import os
import errno

from invoke import run, task
from invoke.util import log


def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise


@task
def vcfify():
  """Convert Excel report into faux VCF"""
  for excel_file in glob('maf/reports/*.xlsx'):
    base = os.path.splitext(os.path.basename(excel_file))[0]
    out_file = "maf/vcfs/%s.vcf" % base
    run("taboo vcfify %(input)s references/base.vcf > %(output)s"
        % dict(input=excel_file, output=out_file))

    log.info("converted %s -> %s" % (excel_file, out_file))


@task
def sort_vcfs():
  """Sort faux VCFs."""
  mkdir_p('maf/vcfs/sorted')

  for vcf_file in glob('maf/vcfs/*.vcf'):
    base = os.path.splitext(os.path.basename(vcf_file))[0]
    out_file = "maf/vcfs/sorted/%s.vcf" % base
    run("vcf-sort %(input)s > %(output)s" % dict(input=vcf_file, output=out_file))

    log.info("sorted %s -> %s" % (vcf_file, out_file))


@task
def split():
  """Split multi-sample VCF into single sample VCFs."""
  for vcf_file in glob('maf/vcfs/sorted/*.vcf'):
    run('taboo split --out=maf/samples/ --pattern="%(sample)s.vcf" {}'.format(vcf_file))

    log.info("split %s" % vcf_file)


@task
def rename():
  """Remove the 'IDX-' prefix that MAF adds to sample IDs."""
  for vcf_file in glob('maf/samples/ID*.vcf'):
    base = os.path.basename(vcf_file)
    unprefixed = base.split('-', 1)[1]
    out_file = "maf/samples/%s" % unprefixed
    os.rename(vcf_file, out_file)

    log.info("renamed %s -> %s" % (vcf_file, out_file))
