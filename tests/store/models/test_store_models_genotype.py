# -*- coding: utf-8 -*-
import pytest

from genotype.exc import UnknownAllelesError


def test_Genotype_alleles(genotypes):
    # GIVEN a genotype record with two different alleles
    genotype = genotypes[1]
    # WHEN accessing them both
    alleles = genotype.alleles
    # THEN they should be returned as a list in sorted order
    assert alleles == ['A', 'G']


def test_Genotype__eq__(genotypes):
    # GIVEN two genotypes with different alleles
    genotype_1, genotype_2 = genotypes[1], genotypes[2]
    # WHEN comparing them
    is_the_same = genotype_1 == genotype_2
    # THEN it should report back as false
    assert is_the_same is False

    # GIVEN two genotypes with the same alleles
    genotype_2 = genotype_1
    # WHEN comparing
    is_the_same = genotype_1 == genotype_2
    # THEN it should report as true
    assert is_the_same is True

    # GIVEN one of the genotypes is of a unknown alleles
    genotype_2 = genotypes['unknown']
    # WHEN comparing
    # THEN it should raise an exception
    with pytest.raises(UnknownAllelesError):
        genotype_1 == genotype_2


def test_Genotype_stringify(genotypes):
    # GIVEN a genotype with different alleles
    genotype = genotypes[1]
    # WHEN stringifying it
    genotype_str = genotype.stringify()
    # THEN it should serialize into a string with sorted alleles
    assert genotype_str == 'AG'


def test_Genotype_is_ok(genotypes):
    # GIVEN a normal genotype record
    genotype = genotypes[1]
    # WHEN checking if there's anything odd with it
    is_ok = genotype.is_ok
    # THEN it should report nothing wrong
    assert is_ok is True

    # GIVEN a genotype with unknown alleles
    unknown_alleles = genotypes['unknown']
    # WHEN checking if it's OK
    is_ok = unknown_alleles.is_ok
    # THEN it should report _not_ OK
    assert is_ok is False
