# -*- coding: utf-8 -*-
from taboo.store.models import Genotype, Sample


def test_Genotype():
    gt = Genotype(rsnumber='rs1044973', allele_1='T', allele_2='A')
    assert str(gt) == 'AT'


def test_Sample():
    sample = Sample(sample_id='sample1', experiment='exp1',
                    source='/tmp/test.vcf', sex='male')
    assert sample.sex == 'male'
