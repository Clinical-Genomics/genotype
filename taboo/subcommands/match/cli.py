# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click

import taboo.match


@click.command()
@click.option('-o', '--origin', default='sequencing')
@click.option('-a', '--alt-origin', default='genotyping')
@click.option('-r', '--references', type=click.File('r'))
@click.argument('sample', type=str)
@click.pass_context
def match(context, sample, references, origin, alt_origin):
    """Match a sample genotype fingerprint against all the rest."""
    comparisons = taboo.match.match_sample(context.parent.store, references, sample,
                                           origin, alt_origin)
    ranked_comparisons = taboo.match.sort_scores(comparisons)

    click.echo('#id\tsample_id\tmismatches')
    for sample, mismatches in ranked_comparisons[:10]:
        click.echo("{sample.id}\t{sample.sample_id}\t{mismatches}"
                   .format(sample=sample, mismatches=mismatches))
