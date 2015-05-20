# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click

from taboo.store.models import Sample, Genotype


@click.command()
@click.argument('samples', nargs=-1, type=str)
@click.pass_context
def show(context, samples):
    """Show genotype strings for multiple samples."""
    query = context.parent.store.session.query
    db_samples = query(Sample).filter(Sample.sample_id.in_(samples))

    click.echo('#id\tsample_id\tgenotypes')
    for sample in db_samples:
        click.echo("{sample.id}\t{sample.sample_id}\t{sample.stringify()}"
                   .format(sample=sample))
