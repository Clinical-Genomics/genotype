# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import click

import taboo.match
import taboo.store
import taboo.rsnumbers
from taboo.store.models import Sample


def stringify_genotypes(genotypes):
    """Stringify genotypes for the sample."""
    return '-'.join(str(genotype) for genotype in genotypes)


@click.command()
@click.argument('samples', nargs=-1, type=str)
@click.option('-r', '--references', type=click.File('r'))
@click.pass_context
def show(context, samples, references):
    """Show genotype strings for multiple samples."""
    query = context.parent.store.session.query
    db_samples = query(Sample).filter(Sample.sample_id.in_(samples))

    if references:
        all_rsnumbers = taboo.store.unique_rsnumbers(query)
        rsnumber_references = taboo.rsnumbers.read(references)
        reference_dict = taboo.rsnumbers.dictify(rsnumber_references)

    rsnumber_columns = '\t'.join(all_rsnumbers)
    click.echo("#id\tsample_id\t{}".format(rsnumber_columns))
    for sample in db_samples:
        if references:
            genotypes = taboo.match.fill_forward(all_rsnumbers, reference_dict,
                                                 sample.genotypes)
        else:
            genotypes = sample.genotypes

        genotype_str = '\t'.join(str(genotype) for genotype in genotypes)
        click.echo("{sample.id}\t{sample.sample_id}\t{genotype_str}"
                   .format(sample=sample, genotype_str=genotype_str))
