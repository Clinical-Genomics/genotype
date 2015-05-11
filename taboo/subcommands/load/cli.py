# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import click

from taboo.input import load_excel, load_vcf


@click.command()
@click.option('-t', '--input-type', type=click.Choice(['vcf', 'excel']))
@click.option('-o', '--origin', type=click.Choice(['genotyping', 'sequencing']))
@click.option('-r', '--rsnumber-path', type=click.Path(exists=True))
@click.argument('input_path', type=click.Path(exists=True))
@click.pass_context
def load(context, input_type, origin, rsnumber_path, input_path):
    """Load database with new samples and genotypes."""
    if input_type == 'vcf':
        load_vcf(context.parent.store, input_path, rsnumber_path, origin=origin)

    else:
        load_excel(context.parent.store, input_path, origin=origin)
