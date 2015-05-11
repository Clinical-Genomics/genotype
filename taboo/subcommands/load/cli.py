# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from taboo.input import load_excel, load_vcf


@click.command()
@click.option('-t', '--input-type', type=click.Choice(['vcf', 'excel']))
@click.option('-o', '--origin', type=click.Choice(['genotyping', 'sequencing']))
@click.argument('input_path', type=click.Path(exists=True))
@click.pass_context
def load(context, input_type, origin, input_path):
    """Load database with new samples and genotypes."""
    loader_func = {'vcf': load_vcf, 'excel': load_excel}.get(input_type)
    loader_func(context.store, input_path, origin=origin)
