# -*- coding: utf-8 -*-
import logging

import click
from sqlalchemy.exc import IntegrityError

from .utils import read_snps

log = logging.getLogger(__name__)


@click.command()
@click.option('-r', '--reset', is_flag=True,
              help='reset database from scratch')
@click.argument('snps', type=click.File('r'))
@click.pass_context
def init(context, reset, snps):
    """Setup a new Taboo database."""
    if reset:
        context.obj['db'].drop_all()

    context.obj['db'].create_all()
    snp_records = read_snps(snps)
    try:
        context.obj['db'].add_commit(*snp_records)
    except IntegrityError:
        log.warn('database already setup with genotypes')
        context.obj['db'].session.rollback()
        context.abort()
