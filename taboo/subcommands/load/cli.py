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
@click.option('-f', '--force', is_flag=True, help='overwrite existing samples')
@click.option('-p', '--prepend', default='ID-')
@click.option('-i', '--include-key', type=str)
@click.argument('input_path', type=click.Path(exists=True))
@click.pass_context
def load(context, input_type, experiment, source, rsnumber_path, force,
         prepend, include_key, input_path):
    """Load database with new samples and genotypes."""
    with codecs.open(rsnumber_path, 'r') as rsnumber_stream:
        if input_type == 'vcf':
            samples = load_vcf(context.parent.store, input_path,
                               rsnumber_stream, experiment=experiment,
                               source=source, force=force)
        else:
            samples = load_excel(context.parent.store, input_path,
                                 experiment=experiment, source=source,
                                 sample_prepend=prepend,
                                 include_key=include_key, force=force)
        for sample in samples:
            pass
