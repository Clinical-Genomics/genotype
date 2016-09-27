# -*- coding: utf-8 -*-
from datetime import date as make_date
import logging

import click
import yaml

from taboo.store import api
from taboo.constants import SEXES, TYPES
from .parsemip import parse_mipsex

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
    sample_obj = api.sample(sample_id, notfound_cb=context.abort)
    if sample:
        log.info("marking sample '%s' as '%s'", sample_id, sample)
        sample_obj.sex = sample
    for analysis_type, sex in analysis:
        log.debug("looking up analysis: '%s-%s'", sample_id, analysis_type)
        analysis_obj = api.analysis(sample_id, analysis_type).first()
        if analysis_obj:
            log.info("marking analysis '%s-%s' as '%s'",
                     analysis_obj.sample_id, analysis_obj.type, sex)
            analysis_obj.sex = sex
        else:
            log.warn("analysis not found: %s-%s", sample_id, analysis_type)
    taboo_db.commit()


@click.command('mip-sex')
@click.option('-s', '--sample', help='limit to a single sample')
@click.argument('qc_metrics', type=click.File('r'))
def mip_sex(sample, qc_metrics):
    """Parse out analysis determined sex of sample."""
    qcm_data = yaml.load(qc_metrics)
    samples_sex = parse_mipsex(qcm_data)
    if sample:
        click.echo(samples_sex[sample], nl=False)
    else:
        for sample_id, sex in samples_sex.items():
            click.echo("{}: {}".format(sample_id, sex))


@click.command()
@click.argument('sample_id')
@click.pass_context
def view(context, sample_id):
    """View added genotypes for all analyses of a sample."""
    sample_obj = api.sample(sample_id, notfound_cb=context.abort)
    click.echo(str(sample_obj))
    for analysis in sample_obj.analyses:
        click.echo(str(analysis))


@click.command()
@click.option('-s', '--since', help='return analysis since date')
@click.option('-l', '--limit', default=20)
@click.option('-o', '--offset', default=0)
@click.option('-m', '--missing', required=True,
              type=click.Choice(['sex', 'genotype', 'sequence']))
@click.pass_context
def ls(context, since, limit, offset, missing):
    """List samples from the database."""
    date_obj = build_date(since) if since else None
    if missing == 'sex':
        query = api.missing_sex(since=date_obj)
    else:
        session = context.obj['db'].session
        query = api.missing_genotypes(session, missing, since=date_obj)

    query = query.offset(offset).limit(limit) if since is None else query
    # sex queries Sample table, genotypes queries Analysis table
    id_key = 'id' if missing == 'sex' else 'sample_id'
    sample_ids = (getattr(record, id_key) for record in query)
    click.echo(" ".join(sample_ids), nl=False)


def build_date(date_str):
    """Parse date out of string."""
    return make_date(*map(int, date_str.split('-')))
