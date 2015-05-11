# -*- coding: utf-8 -*-
from .models import Genotype, Sample


def build_genotype(rsnumber, sample_id, allele_1, allele_2):
    """Build a genotype."""
    return Genotype(rsnumber=rsnumber, sample_id=sample_id, allele_1=allele_1,
                    allele_2=allele_2)


def build_sample(origin, sample_id):
    """Build a sample record."""
    return Sample(sample_id=sample_id, origin=origin)
