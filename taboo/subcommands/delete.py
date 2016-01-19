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
    """Delete a sample from the database."""
    store = context.obj['store']
    exp_types = [experiment] if experiment else EXPERIMENT_TYPES

    for exp_type in exp_types:
        try:
            store.remove(sample_id, exp_type)
            logger.info("removed sample: %s, %s", sample_id, exp_type)
        except NoResultFound:
            logger.warn("couldn't find sample: %s, %s", sample_id, exp_type)
            continue
