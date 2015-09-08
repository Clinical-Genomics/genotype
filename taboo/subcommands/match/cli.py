# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click

from taboo.match import match_sample, sort_scores


@click.command()
@click.option('-e', '--experiment', default='sequencing')
@click.option('-a', '--alt-experiment', default='genotyping')
@click.option('-r', '--references', type=click.File('r'))
@click.argument('sample', type=str)
@click.pass_context
def match(context, sample, references, experiment, alt_experiment):
    """Match a sample genotype fingerprint against all the rest."""
    comparisons = match_sample(context.parent.store, references, sample,
                               experiment, alt_experiment)
    ranked_comparisons = sort_scores(comparisons)

    click.echo('#id\tsample_id\tmatches\tmismatches\tunknowns')
    for sample, results in ranked_comparisons[:10]:
        mismatches = results['mismatch']
        matches = results['match']
        unknowns = results['unknown']
        template = ("{sample.id}\t{sample.sample_id}\t{match}\t{mismatch}"
                    "\t{unknown}")
        click.echo(template.format(sample=sample, match=matches,
                                   mismatch=mismatches, unknown=unknowns))
