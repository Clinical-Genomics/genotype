"""Test the init utilities"""

from genotype.init import utils
from typing import List


def test_read_snp(snp_sequence: List[str]):
    """Test the read snps function"""
    # GIVEN a sequence of TAB-sep lines with SNP info
    nr_rows = len(snp_sequence)

    # WHEN parsing said list
    snps = list(utils.read_snps(snp_sequence))

    # THEN it should return objects for each row
    assert len(snps) == nr_rows

    # first row: rs10144418, T, 14, 55817708
    first_snp = snps[0]
    first_row = snp_sequence[0].split("\t")
    assert first_snp.id == first_row[0]
    assert first_snp.ref == first_row[1]
    assert first_snp.chrom == first_row[2]
    assert first_snp.pos == int(first_row[3])
