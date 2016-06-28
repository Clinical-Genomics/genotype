# -*- coding: utf-8 -*-
import logging

import click

from taboo.store import api
from taboo.constants import SEXES, TYPES

log = logging.getLogger(__name__)


@click.command('add-sex')
@click.option('-s', '--sample', type=click.Choice(SEXES))
@click.option('-a', '--analysis', nargs=2, multiple=True,
              type=(click.Choice(TYPES), click.Choice(SEXES)))
@click.argument('sample_id')
@click.pass_context
def add_sex(context, sample, analysis, sample_id):
    """Add sex determination to samples and analyses."""
    taboo_db = context.obj['db']
    sample_obj = api.sample(taboo_db, sample_id, notfound_cb=context.abort)
    if sample:
        log.info("marking sample '%s' as '%s'", sample_id, sample)
        sample_obj.sex = sample
    for analysis_type, sex in analysis:
        log.debug("looking up analysis: '%s-%s'", sample_id, analysis_type)
        analysis_obj = api.analysis(taboo_db, sample_id, analysis_type).first()
        if analysis_obj:
            log.info("marking analysis '%s-%s' as '%s'",
                     analysis_obj.sample_id, analysis_obj.type, sex)
            analysis_obj.sex = sex
        else:
            log.warn("analysis not found: %s-%s", sample_id, analysis_type)
    taboo_db.commit()


@click.command()
@click.argument('sample_id')
@click.pass_context
def view(context, sample_id):
    """View added genotypes for all analyses of a sample."""
    taboo_db = context.obj['db']
    sample_obj = api.sample(taboo_db, sample_id, notfound_cb=context.abort)
    click.echo(str(sample_obj))
    for analysis in sample_obj.analyses:
        click.echo(str(analysis))
