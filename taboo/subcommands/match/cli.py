# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click

import taboo.match


@click.command()
@click.option('-o', '--origin', default='sequencing')
@click.option('-a', '--alt-origin', default='genotyping')
@click.argument('sample', type=str)
@click.pass_context
def match(context, sample, origin, alt_origin):
    """Match a sample genotype fingerprint against all the rest."""
    matches = taboo.match.match_sample(context.parent.store, sample, origin, alt_origin)
    ranked_matches = taboo.match.sort_ratios(matches)

    click.echo('#id\tsample_id\tratio')
    for sample, ratio in ranked_matches[:10]:
        click.echo("{sample.id}\t{sample.sample_id}\t{ratio}"
                   .format(sample=sample, ratio=ratio))
