# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from datetime import date as make_date
import logging

import json
import click
import yaml

from genotype.store import api, trending
from genotype.constants import SEXES, TYPES
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
    genotype_db = context.obj['db']
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
    genotype_db.commit()


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
@click.option('-m', '--missing',
              type=click.Choice(['sex', 'genotype', 'sequence']))
@click.option('-p', '--plate', help='list all samples on a plate')
@click.option('--no-status', is_flag=True, help='list samples without status')
@click.pass_context
def ls(context, since, limit, offset, missing, plate, no_status):
    """List samples from the database."""

    if missing:
        date_obj = build_date(since) if since else None

        if missing == 'sex':
            query = api.missing_sex(since=date_obj)
        else:
            session = context.obj['db'].session
            query = api.missing_genotypes(session, missing, since=date_obj)
    else:
        query = api.samples(plate_id=plate, no_status=no_status)

    query = query.offset(offset).limit(limit) if since is None else query

    for record in query:
        if hasattr(record, 'sample_id'):
            click.echo(record.sample_id)
        else:
            click.echo(record.id)


@click.command()
@click.argument('sample_id')
@click.pass_context
def sample(context, sample_id):
    """Get a sample from the database."""
    sample_obj = api.sample(sample_id, notfound_cb=context.abort)
    click.echo(sample_obj.status)
    if sample_obj.status != 'pass':
        context.abort()


@click.command('prepare-trending')
@click.option('-s', '--sample-id',
              help='return sample with specific sample id.')
@click.option('-d', '--days',
              help='return samples added a specific number of days ago.')
def prepare_trending(days, sample_id):
    """Get a sample/samples from the database in mongo doc format."""
    sample_dict = {}
    if days:
        some_days_ago = datetime.utcnow() - timedelta(days=int(days))
        samples = api.recent_samples(some_days_ago).all()
        for recent_sample in samples:
            sample_doc = trending.prepare_trending(sample=recent_sample)
            sample_dict[recent_sample.id] = sample_doc
        click.echo(json.dumps(sample_dict))
    elif sample_id:
        sample_doc = trending.prepare_trending(sample_id=sample_id)
        click.echo(sample_doc)
    else:
        log.error('prepare-trending needs to be run with one of the options: (--sample-id/--days)')



def build_date(date_str):
    """Parse date out of string."""
    return make_date(*map(int, date_str.split('-')))
