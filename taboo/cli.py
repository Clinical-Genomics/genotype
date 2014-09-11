# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from codecs import open
from itertools import tee
import os
from subprocess import Popen

import click

from . import __version__
from .compare import pipeline as compare_pipeline
from .extract import pipeline as extract_pipeline
from .filter_vcf import pipeline as filter_vcf_pipeline
from .rename import pipeline as rename_pipeline
from .vcfify import pipeline as vcfify_pipeline
from .utils import namebase

vcf_file_argument = click.argument(
  'vcf_file', type=click.File(encoding='utf-8'), default='-', required=False)
out_option = click.option('--out', type=click.File('w'), default='-')


@click.group()
@click.version_option(__version__)
def cli():
  pass


@cli.command()
@out_option
@click.argument('maf_file', type=click.Path(exists=True))
@vcf_file_argument
def vcfify(maf_file, vcf_file, out):
  """Convert a MAF Excel-file to the standard VCF format."""
  for line in vcfify_pipeline(maf_file, vcf_file):
    click.echo(line, file=out)


@cli.command()
@out_option
@click.argument('rsnumbers_file', type=click.File(encoding='utf-8'))
@vcf_file_argument
def extract(rsnumbers_file, vcf_file, out):
  """Extract variants matching a list of RS numbers."""
  for line in extract_pipeline(vcf_file, rsnumbers_file):
    click.echo(line, file=out)


@cli.command('filter')
@out_option
@vcf_file_argument
def filter_vcf(vcf_file, out):
  """Extract the most interesting information from a VCF-file."""
  for line in filter_vcf_pipeline(vcf_file):
    click.echo(line, file=out)


@cli.command()
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
  vcf_reader, vcf_reader_copy = tee(open(vcf_path, encoding='utf-8'))

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
      Popen(command, shell=True, stdout=handle)


@cli.command()
@click.option('--remove', default='ID-')
@out_option
@click.argument('samples_json', type=click.File(encoding='utf-8'))
@click.argument(
  'vcf_file', type=click.File(encoding='utf-8'), default='-', required=False)
def rename(samples_json, vcf_file, remove, out):
  """Convert sample names using mapping information in a JSON file."""
  for line in rename_pipeline(vcf_file, samples_json, remove_string=remove):
    click.echo(line, file=out)


@cli.command()
@click.argument('complete_vcf', type=click.File(encoding='utf-8'))
@click.argument('incomplete_vcf', type=click.File(encoding='utf-8'))
def compare(complete_vcf, incomplete_vcf):
  """Compare genotypes in two VCF-files.

  Requires input files to be sorted with the same key!

  COMPLETE_VCF: VCF including all variants with genotypes
  INCOMPLETE_VCF: VCF to compare with (can be subset of variants)
  """
  results = compare_pipeline(complete_vcf, incomplete_vcf)

  click.echo("identical\t%s" % results.get(True, 0))
  click.echo("distinct\t%s" % results.get(False, 0))
