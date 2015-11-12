# -*- coding: utf-8 -*-
import codecs

import click

from taboo.input import load_excel, load_vcf


@click.command()
@click.option('-t', '--input-type', type=click.Choice(['vcf', 'excel']))
@click.option('-e', '--experiment', type=click.Choice(['genotyping',
                                                       'sequencing']))
@click.option('-s', '--source', type=str)
@click.option('-r', '--rsnumber-path', type=click.Path(exists=True))
@click.argument('input_path', type=click.Path(exists=True))
@click.pass_context
def load(context, input_type, experiment, source, rsnumber_path, input_path):
    """Load database with new samples and genotypes."""
    if input_type == 'vcf':
        with codecs.open(rsnumber_path, 'r') as rsnumber_stream:
            load_vcf(context.parent.store, input_path, rsnumber_stream,
                     experiment=experiment, source=source)

    else:
        load_excel(context.parent.store, input_path, experiment=experiment,
                   source=source)
