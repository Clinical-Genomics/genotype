# -*- coding: utf-8 -*-
from collections import namedtuple, Counter
import logging

from genotype.compat import zip

log = logging.getLogger(__name__)
Result = namedtuple('Result', ['match', 'mismatch', 'unknown'])


def compare_genotypes(genotype, other_genotype):
    """Compare two genotypes if they have the same alleles."""
    if '0' in genotype.alleles or '0' in other_genotype.alleles:
        return 'unknown'
    elif genotype.alleles == other_genotype.alleles:
        return 'match'
    else:
        return 'mismatch'


def compare_analyses(analysis, other_analysis):
    """Compare and score analyses."""
    genotype_pairs = zip(analysis.genotypes, other_analysis.genotypes)
    results = (compare_genotypes(genotype, other_genotype)
               for genotype, other_genotype in genotype_pairs)
    counter = Counter(results)
    return counter


def check_sample(sample, max_nocalls, min_matches, max_mismatch):
    """Check a sample for inconsistencies."""
    assert len(sample.analyses) == 2, "must load both types of analyses"
    assert sample.sex is not None, "sample must have expected sex or 'unknown'"
    results = {}

    # 1. check no calls from genotyping (could be sign of contamination)
    genotype_analysis = sample.analysis('genotype')
    calls = genotype_analysis.check()
    log.debug("%s - unknown calls: %s", sample.id, calls['unknown'])
    results['nocalls'] = 'fail' if calls['unknown'] >= max_nocalls else 'pass'

    # 2. compare genotypes across analyses (sign of sample mixup)
    result = sample.compare()
    enough_matches = result.get('match', 0) >= min_matches
    ok_mismatches = result.get('mismatch', 0) <= max_mismatch
    results['compare'] = 'pass' if enough_matches and ok_mismatches else 'fail'

    # 3. check sex determinations
    if sample.sex != 'unknown':
        sex_str = '|'.join(list(sample.sexes))
        log.debug("%s - sex determinations: %s", sample.id, sex_str)
        results['sex'] = 'pass' if sample.check_sex() else 'fail'
    else:
        log.debug("unknown sample sex")

    return results
