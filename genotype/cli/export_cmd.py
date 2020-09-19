"""CLI code for commands that interact with the store"""

import json
import logging
from datetime import datetime, timedelta

import click

from genotype.store import api, export

LOG = logging.getLogger(__name__)


@click.command("export-sample")
@click.option(
    "-d", "--days", required=True, help="return samples added within a specific number of days ago."
)
def export_sample(days):
    """Gets data for samples from the sample table, formatted as dict of dicts.

    Returns
        samples_dict(dict): Eg: {"ADM1464A1": {
                                    "status": null,
                                    "sample_created_in_genotype_db": "2019-09-02",
                                    "sex": "female",
                                    "comment": "Lorem ipsum"},
                                "ACC5218A8": {"status": null, ...
                                }
    """
    samples_dict = {}
    some_days_ago = datetime.utcnow() - timedelta(days=int(days))
    samples = api.get_samples_after(some_days_ago).all()
    LOG.info("Getting sample data for %s samples.", str(len(samples)))
    for recent_sample in samples:
        sample_dict = export.get_sample(sample=recent_sample)
        samples_dict[recent_sample.id] = sample_dict
    click.echo(json.dumps(samples_dict))


@click.command("export-sample-analysis")
@click.option(
    "-d", "--days", required=True, help="return samples added within a specific number of days ago."
)
@click.pass_context
def export_sample_analysis(context, days):
    """Gets analysis data for samples from the analysis and genotype tables, formatted as dict
    of dicts.

    Returns:
        dict: Eg: {"ACC2559A1": {   'plate': 'ID43',
                                    'snps': {'genotype': {'rs10144418': ['C', 'C'],...},
                                            'sequence': {'rs10144418': ['T', 'C'], ...},
                                            'comp': {'rs10144418': True, ...}
                                            }
                                    },
                    "ACC5346A3": {'plate': 'ID44',,...
                    }
    """
    samples_dict = {}
    some_days_ago = datetime.utcnow() - timedelta(days=int(days))
    samples = api.get_samples_after(some_days_ago).all()
    LOG.info("Getting analysis data for %s samples.", str(len(samples)))
    session = context.obj["db"].session
    for recent_sample in samples:
        sample_dict = export.get_analysis_equalities(session, sample=recent_sample)
        samples_dict[recent_sample.id] = sample_dict
    click.echo(json.dumps(samples_dict))
