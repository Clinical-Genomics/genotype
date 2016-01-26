# -*- coding: utf-8 -*-
import collections
import logging

import taboo.compat
import taboo.store
import taboo.rsnumbers
from taboo.store.models import Genotype, Result
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

    for rsnumber_id in all_rsnumbers:
        if rsnumber_id in genotype_dict:
            yield genotype_dict[rsnumber_id]

        else:
            rsnumber = reference_dict[rsnumber_id]
            yield Genotype(rsnumber=rsnumber_id, allele_1=rsnumber.ref,
                           allele_2=rsnumber.ref)


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


def match_sample(store, rsnumber_stream, sample_id):
    """Match a sample fingerprint against the database."""
    query = store.session.query

    # get genotypes for the original analysis
    analysis = store.analysis(sample_id, 'sequencing')

    # fill forward missing positions as "ref/ref"
    all_rsnumbers = unique_rsnumbers(query)
    reference_dict = taboo.rsnumbers.parse(rsnumber_stream)
    original_genotypes = list(fill_forward(all_rsnumbers, reference_dict,
                                           analysis.genotypes))

    # walk over all alternative analyses and find best matches
    alt_analyses = store.analyses(experiment='genotyping')
    for alt_analysis in alt_analyses:
        comparisons = compare_genotypes(original_genotypes,
                                        alt_analysis.genotypes)
        results = count_results(comparisons)

        yield alt_analysis, results


def is_success(expected_id, analysis, result, allowed_mismatches=3):
    """Check if a comparison is successful."""
    sample_id = analysis.sample.sample_id
    acceptable_mismatches = result['mismatches'] <= allowed_mismatches
    same_sample = sample_id == expected_id
    if same_sample and acceptable_mismatches:
        logger.debug('genotypes match the same sample')
        answer = True
    else:
        answer = False
        if same_sample and not acceptable_mismatches:
            logger.debug('genotyping has failed on acceptable mismatches (%s)',
                         allowed_mismatches)
        else:
            if acceptable_mismatches:
                logger.debug("genotypes match a different sample: %s", sample_id)
            else:
                logger.debug("genotypes don't match any sample, top: %s", sample_id)
    return answer


def run_comparison(store, rs_stream, sample_id):
    comparisons = match_sample(store, rs_stream, sample_id)
    ranked_comparisons = sort_scores(comparisons)

    top_results = [Result(
                       matches=comparison['match'],
                       mismatches=comparison['mismatch'],
                       unknowns=comparison['unknown'],
                       analysis=analysis
                   ) for analysis, comparison
                   in ranked_comparisons[:5]]
    sample_obj = store.sample(sample_id)

    for result in sample_obj.results:
        store.session.delete(result)
    sample_obj.results = top_results
    store.save()
