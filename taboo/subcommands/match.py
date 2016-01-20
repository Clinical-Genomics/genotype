# -*- coding: utf-8 -*-
import codecs

import click

from taboo.match import run_comparison


@click.command()
@click.option('-e', '--experiment', default='genotyping')
@click.option('-a', '--alt-experiment', default='sequencing')
@click.option('-r', '--reference', type=click.Path(exists=True))
@click.option('-l', '--limit', default=10, help='limit number of results')
@click.argument('sample', type=str)
@click.pass_context
def match(context, sample, reference, experiment, alt_experiment, limit):
    """Match a sample genotype fingerprint against all the rest."""
    store = context.obj['store']
    if reference is None:
        reference = context.obj['rsnumber_ref']

    with codecs.open(reference, 'r') as rs_stream:
        run_comparison(store, rs_stream, sample, experiment, alt_experiment)
