# -*- coding: utf-8 -*-
from genotype.store.models import Sample


SAMPLE = Sample(id='ADM12')
SAMPLE_FILLED_IN = Sample(id='ADM13', sex='female', status='PASS')


def test___str__():
    # GIVEN a very basic sample without information
    sample = SAMPLE
    # WHEN serializing it as a string
    sample_str = str(sample)
    # THEN it should return a string with placeholders
    assert sample_str == "{}\t[status]\t[sex]".format(sample.id)
