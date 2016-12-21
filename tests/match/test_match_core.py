# -*- coding: utf-8 -*-
from genotype.match import core
from genotype.store.models import Analysis, Genotype


def test_compare_genotypes(genotypes):
    # GIVEN two identical genotypes (sample alleles)
    genotype_1 = genotypes[1]
    # WHEN comparing them
    result = core.compare_genotypes(genotype_1, genotype_1)
    # THEN the result should be a 'match'
    assert result == 'match'

    # GIVEN two genotypes with different alleles
    genotype_1, genotype_2 = genotypes[1], genotypes[2]
    # WHEN comparing them
    result = core.compare_genotypes(genotype_1, genotype_2)
    # THEN the result should be a 'mismatch'
    assert result == 'mismatch'

    # GIVEN genotypes where one of them contains unknown allele(s)
    genotype_1, genotype_2 = genotypes[1], genotypes['unknown']
    # WHEN comparing them
    result = core.compare_genotypes(genotype_1, genotype_2)
    # THEN the result should be a 'unknown'
    assert result == 'unknown'


def test_compare_analyses():
    # GIVEN two analyses with different genotypes
    genotypes = [Genotype(rsnumber='1', allele_1='A', allele_2='T'),
                 Genotype(rsnumber='2', allele_1='C', allele_2='C')]
    analysis = Analysis(type='genotype', genotypes=genotypes)

    other_genotypes = [Genotype(rsnumber='1', allele_1='A', allele_2='A'),
                       Genotype(rsnumber='2', allele_1='C', allele_2='C')]
    other_analysis = Analysis(type='sequence', genotypes=other_genotypes)
    # WHEN comparing them
    counter = core.compare_analyses(analysis, other_analysis)
    # THEN it should return the counts for the matches/mismatches
    assert counter['match'] == 1
    assert counter['mismatch'] == 1


def test_check_sample():
    pass
