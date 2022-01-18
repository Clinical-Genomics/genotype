"""Cli command to delete stuff from database"""

import logging

import click

from genotype.constants import TYPES
from genotype.store import api
from genotype.store.models import Sample
from genotype.store.models import User

LOG = logging.getLogger(__name__)


@click.command("delete")
@click.option("-a", "--analysis", type=click.Choice(TYPES))
@click.argument("sample_id")
@click.pass_context
def delete_cmd(context, analysis, sample_id):
    """Delete analyses and samples from the database."""
    genotype_db = context.obj["db"]
    if analysis:
        LOG.info("deleting analysis: %s, %s", sample_id, analysis)
        old_analysis = api.analysis(sample_id, analysis).first()
        if old_analysis is None:
            LOG.error("analysis not loaded in database")
            raise click.Abort
        api.delete_analysis(genotype_db, old_analysis)
        return

    LOG.info("deleting sample: %s", sample_id)
    old_sample = Sample.query.get(sample_id)
    if old_sample is None:
        LOG.error("sample not loaded in database")
        raise click.Abort
    old_sample.delete()
    genotype_db.commit()


@click.command("delete-user")
@click.argument("email")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def delete_user(context, email, dry_run):
    """Delete user from the database."""
    genotype_db = context.obj["db"]

    LOG.info("Inactivating user: %s", email)
    user = User.query.filter(User.email == email).first()
    if user is None:
        LOG.error("User %s not present in database" % email)
        raise click.Abort

    if dry_run:
        LOG.info("Dry-run -> no changes!")
        raise click.Abort

    user.email = f"_{user.email}"
    genotype_db.commit()
