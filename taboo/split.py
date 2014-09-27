# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from codecs import open
import itertools
import os
import subprocess

import click

from .utils import namebase


@click.command()
@click.option('--out', type=click.Path(exists=True), default='./')
@click.option('--pattern', default="%(sample)s.%(base)s.vcf",
  help='Sample file naming pattern')
@click.option('--sample', type=str, help='Single sample id to extract')
@click.argument('vcf_path', type=click.Path(exists=True))
def split(vcf_path, sample, out, pattern):
  """Split VCF-file into multiple single sample VCF-files.

  \b
  VCF_FILE: path to VCF file with multiple samples

  Principle:

    $ vcf-subset -c <SAMPLE> <VCF_FILE> > <OUT+PATTERN>
  """
  # figure out the name base of the VCF-file
  file_base = namebase(vcf_path)

  # base of vcf-subset command to execute per sample id
  base_command = 'vcf-subset --keep-uncalled -c %(sample)s %(file)s'

  # spawn two csv readers
  vcf_reader, vcf_reader_copy = itertools.tee(open(vcf_path, encoding='utf-8'))

  # figure out which samples are in the VCF file
  for line in vcf_reader_copy:
    if line.startswith('#CHROM'):
      samples = line.strip().split('\t')[9:]
      break

  for sample in samples:
    # build path and name of output file
    save_file = pattern % dict(sample=sample, base=file_base)
    save_path = os.path.join(out, save_file)

    # compose UNIX command
    command = base_command % dict(sample=sample, file=vcf_path)

    # open a file to write to
    with open(save_path, 'w', encoding='utf-8') as handle:
      # execute the command in the shell, redirecting stdout to file
      subprocess.Popen(command, shell=True, stdout=handle)
