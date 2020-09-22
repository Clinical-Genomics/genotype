"""Tests for load vcf functionality"""

from pathlib import Path
from typing import List

from genotype.load import vcf as vcf_mod
from genotype.store.models import SNP, Analysis


def test_load_vcf(bcf_path: Path, snps: List[SNP]):
    """Test to load a vcf"""
    # GIVEN a BCF file with one sample and a list of SNP records
    sample_id = "000139T"
    nr_snps = len(snps)

    # WHEN building sequence analyses records
    analyses = list(vcf_mod.load_vcf(vcf_file=str(bcf_path), snps=snps))

    # THEN it should return a new analysis object and link to the sample
    assert len(analyses) == 1
    analysis = analyses[0]
    assert isinstance(analysis, Analysis)
    assert analysis.sample_id == sample_id
    assert analysis.sample is None
    assert len(analysis.genotypes) == nr_snps
