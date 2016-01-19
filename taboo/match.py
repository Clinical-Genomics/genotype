# -*- coding: utf-8 -*-
import collections
import logging

import taboo.compat
import taboo.store
import taboo.rsnumbers
from taboo.store.models import Sample, Genotype
from taboo.utils import unique_rsnumbers

logger = logging.getLogger(__name__)


def sort_scores(scores):
    """Sort matches based on comparison scores.

    Args:
        scores (list): list of matches from comparison

    Returns:
        list: sorted matches based on 'match' score
    """
    return sorted(scores, key=lambda item: item[1]['match'], reverse=True)


def fill_forward(all_rsnumbers, reference_dict, genotypes):
    """Fill forward missing rsnumbers as ref/ref."""
    genotype_dict = {genotype.rsnumber: genotype for genotype in genotypes}

    for rsnumber in all_rsnumbers:
        if rsnumber in genotype_dict:
            yield genotype_dict[rsnumber]

        else:
            reference = reference_dict[rsnumber]
            yield Genotype(rsnumber=rsnumber, allele_1=reference,
                           allele_2=reference)


def compare_genotypes(original, alternative):
    """Compare a list of genotypes against a list of alternative genotypes.

    Returns the number of mismatches based soley on identity.
    """
    for org_gt, alt_gt in taboo.compat.zip(original, alternative):
        if alt_gt.allele_1 == '0':
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


def match_sample(store, rsnumber_stream, sample_id, experiment='sequencing',
                 alt_experiment='genotyping'):
    """Match a sample fingerprint against the database."""
    query = store.session.query

    # get genotypes for the original sample
    sample = query(Sample).filter_by(sample_id=sample_id,
                                     experiment=experiment).one()

    # fill forward missing positions as "ref/ref"
    all_rsnumbers = unique_rsnumbers(query)
    reference_dict = taboo.rsnumbers.parse(rsnumber_stream)
    original_genotypes = list(fill_forward(all_rsnumbers, reference_dict,
                                           sample.genotypes))

    # walk over all alternative samples and find best matches
    alt_samples = query(Sample).filter_by(experiment=alt_experiment)
    for alt_sample in alt_samples:
        comparisons = compare_genotypes(original_genotypes,
                                        alt_sample.genotypes)
        results = count_results(comparisons)

        yield alt_sample, results


def compare_sample(comparisons, sample_id, allowed_mismatches=3):
    """Compare genotyping for a sample and update the status."""
    top_sample, top_result = comparisons[0]
    acceptable_mismatches = top_result['mismatches'] <= allowed_mismatches
    same_sample = top_sample.sample_id == sample_id
    if same_sample and acceptable_mismatches:
        logger.info('genotypes match the same sample')
        is_success = True
    else:
        is_success = False
        if same_sample and not acceptable_mismatches:
            logger.warn('genotyping has failed on acceptable mismatches (%s)',
                        allowed_mismatches)
        else:
            if acceptable_mismatches:
                logger.error("genotypes match a different sample: %s",
                             top_sample.sample_id)
            else:
                logger.error("genotypes don't match any sample, top: %s",
                             top_sample.sample_id)
    return is_success
