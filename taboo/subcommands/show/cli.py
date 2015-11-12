# -*- coding: utf-8 -*-
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
@click.option('-s', '--skip', default=0)
@click.option('-r', '--references', type=click.File('r'), required=True)
@click.pass_context
def show(context, samples, skip, references):
    """Show genotype strings for multiple samples."""
    query = context.parent.store.session.query
    db_samples = query(Sample)
    if samples:
        db_samples = db_samples.filter(Sample.sample_id.in_(samples))

    rsnumber_references = taboo.rsnumbers.read(references)
    reference_dict = taboo.rsnumbers.dictify(rsnumber_references)

    all_rsnumbers = taboo.store.unique_rsnumbers(query)
    rsnumber_columns = '\t'.join(all_rsnumbers)
    click.echo("#id\tsample_id\texperiment\t{}".format(rsnumber_columns))

    template = ("{sample.id}\t{sample.sample_id}\t{sample.experiment}"
                "\t{genotype_str}")
    for sample in db_samples:
        genotypes = taboo.match.fill_forward(all_rsnumbers, reference_dict,
                                             sample.genotypes)
        genotype_str = '\t'.join(str(genotype) for genotype in genotypes)
        click.echo(template.format(sample=sample, genotype_str=genotype_str))
