# -*- coding: utf-8 -*-
import fuzzywuzzy.fuzz

import taboo.store
from taboo.store.models import Sample, Genotype


def stringify_genotypes(genotypes):
    """Stringify a list of genotypes."""
    return '-'.join(str(genotype) for genotype in genotypes)


def sort_ratios(ratios):
    """Sort matches based on comparison ratios."""
    return sorted(ratios, key=lambda item: item[1], reverse=True)


def perfect_match(ratios):
    """Find best match."""
    for sample, ratio in ratios:
        if ratio == 100:
            return sample, ratio


def match_sample(store, sample_id, origin='sequencing', compare_origin='maf'):
    """Match a sample fingerprint against the database."""
    query = store.session.query
    sample = query(Sample).filter_by(sample_id=sample_id, origin=origin).one()
    alt_samples = query(Sample).filter_by(origin=compare_origin)

    genotypes = query(Genotype).filter_by(sample_id=sample.id).order_by('rsnumber')
    fingerprint = stringify_genotypes(genotypes)

    for alt_sample in alt_samples:
        alt_genotypes = query(Genotype).filter_by(sample_id=alt_sample.id)\
                                       .order_by('rsnumber')
        alt_fingerprint = stringify_genotypes(alt_genotypes)

        # compare the fingerprints
        ratio = fuzzywuzzy.fuzz.ratio(fingerprint, alt_fingerprint)

        yield alt_sample, ratio
