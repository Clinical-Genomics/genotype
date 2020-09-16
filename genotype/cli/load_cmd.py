"""Cli load command"""

import logging

import click


from genotype.store import api
from genotype.load.vcf import load_vcf
from genotype.load.excel import load_excel

LOG = logging.getLogger(__name__)


@click.command("load")
@click.option("-k", "--include-key", help="prefix for relevant samples")
@click.option("-f", "--force", is_flag=True)
@click.argument("input_file", type=click.File("rb"))
@click.pass_context
def load_cmd(context, include_key, force, input_file):
    """Load data from genotype resources."""
    database_api = context.obj["db"]
    if input_file.name.endswith(".xlsx"):
        LOG.info("loading analyses from Excel book: %s", input_file.name)
        analyses = load_excel(input_file.name, input_file.read(), include_key=include_key)
    elif input_file.name.endswith(".bcf") or input_file.name.endswith(".vcf.gz"):
        LOG.info("loading analyses from VCF file: %s", input_file.name)
        snps = api.snps()
        analyses = load_vcf(input_file.name, snps)

    for analysis in analyses:
        LOG.debug("loading analysis for sample: %s", analysis.sample_id)
        is_saved = api.add_analysis(genotype_db, analysis, replace=force)
        if is_saved:
            LOG.info("loaded analysis for sample: %s", analysis.sample_id)
        else:
            LOG.warning("found previous analysis, skip: %s", analysis.sample_id)
