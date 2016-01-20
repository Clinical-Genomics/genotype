# -*- coding: utf-8 -*-
import logging

import click
from sqlalchemy.orm.exc import NoResultFound

from taboo.constants import EXPERIMENT_TYPES

logger = logging.getLogger(__name__)


@click.command()
@click.option('-e', '--experiment', type=click.Choice(EXPERIMENT_TYPES))
@click.argument('sample_id')
@click.pass_context
def delete(context, sample_id, experiment):
    """Delete a sample or specific analysis from the database."""
    store = context.obj['store']

    try:
        if experiment:
            store.remove(sample_id, experiment)
            logger.info("removed analysis: %s, %s", sample_id, experiment)
        else:
            store.remove_sample(sample_id)
            logger.info("removed sample: %s", sample_id)
    except NoResultFound:
        logger.warn("couldn't find sample: %s, %s", sample_id, experiment)
        context.abort()
