# -*- coding: utf-8 -*-
import collections

import taboo._compat
import taboo.store
import taboo.rsnumbers
from taboo.store.models import Sample, Genotype


def sort_scores(scores):
    """Sort matches based on comparison scores."""
    return sorted(scores, key=lambda item: item[1]['match'])


def fill_forward(all_rsnumbers, reference_dict, genotypes):
    """Fill forward missing rsnumbers as ref/ref."""
    genotype_dict = {genotype.rsnumber: genotype for genotype in genotypes}

    for rsnumber in all_rsnumbers:
        if rsnumber in genotype_dict:
            yield genotype_dict[rsnumber]

        else:
            reference = reference_dict[rsnumber]
            yield Genotype(rsnumber=rsnumber, allele_1=reference, allele_2=reference)


def compare_genotypes(original, alternative):
    """Compare a list of genotypes against a list of alternative genotypes.

    Returns the number of mismatches based soley on identity.
    """
    for org_gt, alt_gt in taboo._compat.zip(original, alternative):
        if alt_gt.allele_1 != '0':
            # no comparison
            yield 'unknown'
        elif str(org_gt) != str(alt_gt):
            # genotypes are *not* identical
            yield 'mismatch'
        else:
            # genotypes are identical
            yield 'match'


def count_results(comparisons):
    """Tally the results from the comparison."""
    counter = collections.Counter(comparisons)
    return counter


def match_sample(store, rsnumber_stream, sample_id, origin='sequencing',
                 compare_origin='maf'):
    """Match a sample fingerprint against the database."""
    query = store.session.query

    # get genotypes for the original sample
    sample = query(Sample).filter_by(sample_id=sample_id, origin=origin).one()

    # fill forward missing positions as "ref/ref"
    all_rsnumbers = taboo.store.unique_rsnumbers(query)
    rsnumber_references = taboo.rsnumbers.read(rsnumber_stream)
    reference_dict = taboo.rsnumbers.dictify(rsnumber_references)
    original_genotypes = list(fill_forward(all_rsnumbers, reference_dict,
                                           sample.genotypes))

    # walk over all alternative samples and find best matches
    alt_samples = query(Sample).filter_by(origin=compare_origin)
    for alt_sample in alt_samples:
        comparisons = compare_genotypes(original_genotypes, alt_sample.genotypes)
        results = count_results(comparisons)

        yield alt_sample, results
