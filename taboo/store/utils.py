# -*- coding: utf-8 -*-
from .models import Genotype


def build_genotype(rsnumber, sample_id, allele_1, allele_2):
    """Build a genotype."""
    return Genotype(rsnumber=rsnumber, sample_id=sample_id, allele_1=allele_1,
                    allele_2=allele_2)


def unique_rsnumbers(query):
    """Fecth a list of distinct rsnumbers loaded in the database."""
    results = query(Genotype.rsnumber).distinct().order_by(Genotype.rsnumber)

    # just extract the only field from the list of tuples
    rs_ids = [result[0] for result in results]

    return rs_ids
