# -*- coding: utf-8 -*-
import codecs

import click

from taboo.constants import EXPERIMENT_TYPES
import taboo.match
import taboo.store
import taboo.rsnumbers
from taboo.utils import unique_rsnumbers


def stringify_genotypes(genotypes):
    """Stringify genotypes for the sample."""
    return '-'.join(str(genotype) for genotype in genotypes)


@click.command()
@click.option('-e', '--experiment', type=click.Choice(EXPERIMENT_TYPES))
@click.option('-s', '--source', type=str)
@click.option('--skip', default=0)
@click.option('-r', '--reference', type=click.Path(exists=True))
@click.argument('samples', nargs=-1, type=str)
@click.pass_context
def show(context, samples, experiment, source, skip, reference):
    """Show genotype strings for multiple samples."""
    store = context.obj['store']
    if reference is None:
        reference = context.obj['rsnumber_ref']

    db_samples = store.samples(sample_ids=samples, experiment=experiment,
                               source=source)

    with codecs.open(reference, 'r') as ref_handle:
        reference_dict = taboo.rsnumbers.parse(ref_handle)

    all_rsnumbers = unique_rsnumbers(store.session.query)
    rsnumber_columns = '\t'.join(all_rsnumbers)
    click.echo("#id\tsample_id\texperiment\tsource\t{}"
               .format(rsnumber_columns))

    template = ("{sample.id}\t{sample.sample_id}\t{sample.experiment}\t"
                "{sample.source}\t{genotype_str}")
    for sample in db_samples:
        genotypes = taboo.match.fill_forward(all_rsnumbers, reference_dict,
                                             sample.genotypes)
        genotype_str = '\t'.join(str(genotype) for genotype in genotypes)
        click.echo(template.format(sample=sample, genotype_str=genotype_str))
