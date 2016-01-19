# -*- coding: utf-8 -*-
import codecs
import logging

import click

from taboo.input import load_excel, load_vcf

logger = logging.getLogger(__name__)


@click.command()
@click.option('-t', '--input-type', type=click.Choice(['vcf', 'excel']))
@click.option('-f', '--force', is_flag=True, help='overwrite existing samples')
@click.option('-i', '--include-key', default='-CG-')
@click.argument('input_file', type=click.Path(exists=True))
@click.pass_context
def load(context, input_type, force, include_key, input_file):
    """Load a sample into the database."""
    db = context.obj['store']

    if input_type is None:
        # guess
        if input_file.endswith('.vcf'):
            input_type = 'vcf'
        elif input_file.endswith('.xlsx'):
            input_type = 'excel'
        else:
            logger.error('unknown file format')
            context.abort()

    with codecs.open(context.obj['rsnumber_ref']) as rs_stream:
        if input_type == 'vcf':
            samples = load_vcf(db, input_file, rs_stream, force=force)
        else:
            samples = load_excel(db, input_file, include_key=include_key,
                                 force=force)

        for sample in samples:
            logger.info("added samples: %s", sample.sample_id)
