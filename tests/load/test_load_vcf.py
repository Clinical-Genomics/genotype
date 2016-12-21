# -*- coding: utf-8 -*-
from genotype.load import vcf as vcf_mod
from genotype.store.models import Analysis


def test_load_vcf(bcf_path, snps):
    # GIVEN a BCF file with one sample and a list of SNP records
    sample_id = '000139T'
    no_snps = len(snps)
    # WHEN building sequence analyses records
    analyses = list(vcf_mod.load_vcf(bcf_path, snps))
    # THEN it should return a new analysis object and link to the sample
    assert len(analyses) == 1
    analysis = analyses[0]
    assert isinstance(analysis, Analysis)
    assert analysis.sample_id == sample_id
    assert analysis.sample is None
    assert len(analysis.genotypes) == no_snps
