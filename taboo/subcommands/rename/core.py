# -*- coding: utf-8 -*-
import json

from toolz import concatv


def pipeline(vcf_stream, samples_json, remove_string=''):
  # sample conversion dict (JSON)
  samples = json.load(samples_json)

  for line in vcf_stream:
    stripped = line.strip()
    if stripped.startswith('#CHROM'):
      parts = stripped.split('\t')

      # replace the ID or re-use it if it wasn't found in the sample
      # conversion dict.
      sample_ids = [samples.get(sample.replace(remove_string, ''), sample)
                    for sample in parts[9:]]

      yield '\t'.join(concatv(parts[:9], sample_ids))

    else:
      yield stripped
