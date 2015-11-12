# -*- coding: utf-8 -*-
import logging

import click

logger = logging.getLogger(__name__)


def setup_db(store, reset=False):
    """Configure a new database from scratch."""
    if reset:
        store.tear_down()
    store.setup()
    return store


@click.command()
@click.option('-r', '--reset', is_flag=True)
@click.pass_context
def setup(context, reset):
    """Configure a new database from scratch."""
    logger.info('Configuring new database...')
    setup_db(context.parent.store, reset=reset)
