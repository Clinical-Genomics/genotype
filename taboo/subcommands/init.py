# -*- coding: utf-8 -*-
import logging

import click

logger = logging.getLogger(__name__)


@click.command()
@click.option('-r', '--reset', is_flag=True)
@click.pass_context
def init(context, reset):
    """Initialize a new setup of taboo."""
    logger.info("configure new database: %s", context.obj['store'].db_uri)
    # setup database with tables
    context.obj['store'].setup(reset=reset)
