# -*- coding: utf-8 -*-
import codecs

import click

from taboo.match import match_sample, sort_scores, compare_sample


@click.command()
@click.option('-e', '--experiment', default='sequencing')
@click.option('-a', '--alt-experiment', default='genotyping')
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
        comparisons = match_sample(store, rs_stream, sample,
                                   experiment, alt_experiment)
        ranked_comparisons = sort_scores(comparisons)

    is_success = compare_sample(ranked_comparisons, sample)
    click.echo("#{}".format('success' if is_success else 'fail'))
    click.echo('#id\tsample_id\tmatches\tmismatches\tunknowns')
    for sample, results in ranked_comparisons[:limit]:
        mismatches = results['mismatch']
        matches = results['match']
        unknowns = results['unknown']
        template = ("{sample.id}\t{sample.sample_id}\t{match}\t{mismatch}"
                    "\t{unknown}")
        click.echo(template.format(sample=sample, match=matches,
                                   mismatch=mismatches, unknown=unknowns))
