# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click


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
    click.echo('Configuring new database...')
    setup_db(context.parent.store, reset=reset)
