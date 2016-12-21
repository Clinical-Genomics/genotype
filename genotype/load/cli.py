# -*- coding: utf-8 -*-
import logging

import click

from genotype.constants import TYPES
from genotype.store.models import Sample
from genotype.store import api
from .vcf import load_vcf
from .excel import load_excel

log = logging.getLogger(__name__)


@click.command()
@click.option('-k', '--include-key', help='prefix for relevant samples')
@click.option('-f', '--force', is_flag=True)
@click.argument('input_file', type=click.File())
@click.pass_context
def load(context, include_key, force, input_file):
    """Load data from genotype resources."""
    genotype_db = context.obj['db']
    if input_file.name.endswith('.xlsx'):
        log.info('loading analyses from Excel book: %s', input_file.name)
        analyses = load_excel(input_file.name, input_file.read(),
                              include_key=include_key)
    elif input_file.name.endswith('.bcf') or input_file.name.endswith('.vcf.gz'):
        log.info('loading analyses from VCF file: %s', input_file.name)
        snps = api.snps()
        analyses = load_vcf(input_file.name, snps)

    for analysis in analyses:
        log.debug('loading analysis for sample: %s', analysis.sample_id)
        is_saved = api.add_analysis(genotype_db, analysis, replace=force)
        if is_saved:
            log.info('loaded analysis for sample: %s', analysis.sample_id)
        else:
            log.warn('found previous analysis, skip: %s', analysis.sample_id)


@click.command()
@click.option('-a', '--analysis', type=click.Choice(TYPES))
@click.argument('sample_id')
@click.pass_context
def delete(context, analysis, sample_id):
    """Delete analyses and samples from the database."""
    genotype_db = context.obj['db']
    if analysis:
        log.info("deleting analysis: %s, %s", sample_id, analysis)
        old_analysis = api.analysis(sample_id, analysis).first()
        if old_analysis is None:
            log.error("analysis not loaded in database")
            context.abort()
        api.delete_analysis(genotype_db, old_analysis)
    else:
        log.info("deleting sample: %s", sample_id)
        old_sample = Sample.query.get(sample_id)
        if old_sample is None:
            log.error("sample not loaded in database")
            context.abort()
        old_sample.delete()
        genotype_db.commit()
