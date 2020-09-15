"""Cli command to initialize a new database"""

import logging

import click
from sqlalchemy.exc import IntegrityError

from genotype.init.utils import read_snps

LOG = logging.getLogger(__name__)


@click.command("init")
@click.option('-r', '--reset', is_flag=True,
              help='reset database from scratch')
@click.argument('snps', type=click.File('r'))
@click.pass_context
def init_cmd(context, reset, snps):
    """Setup a new Genotype database."""
    LOG.info("Running init database")
    database_api = context.obj['db']
    if reset:
        database_api.drop_all()

    database_api.create_all()
    snp_records = read_snps(snps)
    try:
        database_api.add_commit(*snp_records)
    except IntegrityError:
        LOG.warning('database already setup with genotypes')
        database_api.session.rollback()
        raise click.Abort
