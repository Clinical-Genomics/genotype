# -*- coding: utf-8 -*-
from taboo.load import bcf as bcf_mod
from taboo.store.models import Analysis


def test_parse_sampleids(bcf):
    # GIVEN a BCF file with one sample
    sample_id = '000139T'
    # WHEN parsing out sample info
    samples_ids = list(bcf_mod.parse_sampleids(bcf))
    # THEN it should return a single sample
    assert len(samples_ids) == 1
    assert samples_ids[0] == sample_id


def test_load_bcf(bcf_path, snps):
    # GIVEN a BCF file with one sample and a list of SNP records
    sample_id = '000139T'
    no_snps = len(snps)
    # WHEN building sequence analyses records
    analyses = list(bcf_mod.load_bcf(bcf_path, snps))
    # THEN it should return a new analysis object and link to the sample
    assert len(analyses) == 1
    analysis = analyses[0]
    assert isinstance(analysis, Analysis)
    assert analysis.sample_id == sample_id
    assert analysis.sample is None
    assert len(analysis.genotypes) == no_snps
