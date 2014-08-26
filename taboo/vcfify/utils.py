# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import csv
from datetime import date

from toolz import map

from .. import __version__
from .._compat import text_type


def vcf_headers(samples):
  # meta data
  yield '##fileformat=VCFv4.2'
  yield "##fileDate=%s" % text_type(date.today()).replace('-', '')
  yield "##source=typerV%s" % __version__
  yield "##reference=unknown"

  # contigs/chromosomes
  yield '##contig=<ID=1,length=249250621>'
  yield '##contig=<ID=2,length=243199373>'
  yield '##contig=<ID=3,length=198022430>'
  yield '##contig=<ID=4,length=191154276>'
  yield '##contig=<ID=5,length=180915260>'
  yield '##contig=<ID=6,length=171115067>'
  yield '##contig=<ID=7,length=159138663>'
  yield '##contig=<ID=8,length=146364022>'
  yield '##contig=<ID=9,length=141213431>'
  yield '##contig=<ID=10,length=135534747>'
  yield '##contig=<ID=11,length=135006516>'
  yield '##contig=<ID=12,length=133851895>'
  yield '##contig=<ID=13,length=115169878>'
  yield '##contig=<ID=14,length=107349540>'
  yield '##contig=<ID=15,length=102531392>'
  yield '##contig=<ID=16,length=90354753>'
  yield '##contig=<ID=17,length=81195210>'
  yield '##contig=<ID=18,length=78077248>'
  yield '##contig=<ID=19,length=59128983>'
  yield '##contig=<ID=20,length=63025520>'
  yield '##contig=<ID=21,length=48129895>'
  yield '##contig=<ID=22,length=51304566>'
  yield '##contig=<ID=X,length=155270560>'
  yield '##contig=<ID=Y,length=59373566>'
  yield '##contig=<ID=MT,length=16569>'

  # genotype call format
  yield '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">'

  # samples
  required = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT'
  samples_str = '\t'.join(map(str, samples[1:]))
  yield "%(cols)s\t%(samples)s" % dict(cols=required, samples=samples_str)


def rsnumber_converter(vcf_stream):
  """Convert from a given rsnumber to genomic positions."""
  # build dict mapping rsnumbers to variant lines (list)
  dictionary = {}
  for variant in csv.reader(vcf_stream, delimiter='\t'):
    dictionary[variant[2]] = variant

  def getter(rsnumber, default=None):
    return dictionary.get(rsnumber, default)

  return getter


def encode_genotype(ref, alt, alleles):
  """Encode MAF genotypes into VCF genotypes."""
  mapper = {
    '0': '.',
    ref: '0',
    alt: '1',
  }

  return [mapper.get(allele, '2') for allele in alleles]
