"""Cli load command"""

import logging
from pathlib import Path

import click

from genotype.load.excel import load_excel
from genotype.load.vcf import load_vcf
from genotype.store import api

LOG = logging.getLogger(__name__)


@click.command("load")
@click.option("-k", "--include-key", help="prefix for relevant samples")
@click.option("-f", "--force", is_flag=True)
@click.argument("input_file", type=click.Path(exists=True))
@click.pass_context
def load_cmd(context, include_key, force, input_file):
    """Load data from genotype resources."""
    input_path = Path(input_file)
    database_api = context.obj["db"]
    if input_path.suffix == ".xlsx":
        LOG.info("loading analyses from Excel book: %s", input_path.name)
        with open(input_path, "rb") as infile:
            analyses = load_excel(
                file_path=input_path.name, file_contents=infile.read(), include_key=include_key
            )
    elif input_path.suffix == ".bcf" or input_path.name.endswith(".vcf.gz"):
        LOG.info("loading analyses from VCF file: %s", input_path.name)
        snps = api.snps()
        analyses = load_vcf(vcf_file=input_file, snps=snps)
    else:
        LOG.warning("unknown input format: %s", input_file)
        raise click.Abort

    for analysis in analyses:
        LOG.debug("loading analysis for sample: %s", analysis.sample_id)
        is_saved = api.add_analysis(db=database_api, new_analysis=analysis, replace=force)
        if is_saved:
            LOG.info("loaded analysis for sample: %s", analysis.sample_id)
        else:
            LOG.warning("found previous analysis, skip: %s", analysis.sample_id)
