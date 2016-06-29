# -*- coding: utf-8 -*-
import logging
import math

import click

from taboo.constants import TYPES
from taboo.store.models import Analysis
from taboo.store import api
from .core import compare_analyses

log = logging.getLogger(__name__)


def log_result(sample_id, result):
    total_snps = api.snps().count()
    cutoff = math.floor(total_snps / 5)
    if result.get('mismatch') == 0 or result.get('mismatch') <= cutoff:
        log_func = log.info
    else:
        log_func = log.warn
    template = ("{sample} | matches: {match}, mismatches: {mismatch}, "
                "unknown: {unknown}")
    log_func(template.format(sample=sample_id,
                             match=result.get('match', 0),
                             mismatch=result.get('mismatch', 0),
                             unknown=result.get('unknown', 0)))


@click.command()
@click.argument('sample_id')
@click.option('-a', '--analysis', default='genotype', type=click.Choice(TYPES))
@click.pass_context
def match(context, sample_id, analysis):
    """Match genotypes for an analysis against all samples."""
    sample_obj = api.sample(sample_id, notfound_cb=context.abort)
    analysis_obj = sample_obj.analysis(analysis)
    other_analyses = Analysis.query.filter(Analysis.type != analysis)
    for other_analysis in other_analyses:
        result = compare_analyses(analysis_obj, other_analysis)
        log_result(other_analysis.sample_id, result)


@click.command()
@click.argument('sample_id')
@click.pass_context
def check(context, sample_id):
    """Check integrity of a sample."""
    sample_obj = api.sample(sample_id, notfound_cb=context.abort)

    # 1. check no calls from genotyping (could be sign of contamination)
    total_snps = api.snps().count()
    cutoff = math.floor(total_snps / 3)
    genotype_analysis = sample_obj.analysis('genotype')
    if genotype_analysis:
        calls = genotype_analysis.check()
        if calls['unknown'] >= cutoff:
            log.warn("genotyping: fail (%s no-calls)", calls['unknown'])
        else:
            log.debug("no-calls from genotyping: %s", calls['unknown'])
    else:
        log.debug('no genotyping analysis loaded')

    # 2. compare genotypes across analyses (sign of sample mixup)
    if len(sample_obj.analyses) == 2:
        result = sample_obj.compare()
        log_result(sample_id, result)
    else:
        log.debug("analyses for samples not loaded")

    # 3. check sex determinations
    if sample_obj.sex and sample_obj.sex is not 'unknown':
        if sample_obj.check_sex():
            log.info("sex determination: pass")
        else:
            sex_str = '|'.join(list(sample_obj.sexes))
            log.warn("sex determination: fail (%s)", sex_str)
    else:
        log.debug("unknown sample sex")
