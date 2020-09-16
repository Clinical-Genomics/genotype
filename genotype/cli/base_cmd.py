"""Code for the base of the CLI"""

import codecs
import logging
import os

import click
import coloredlogs
import yaml

from genotype import __title__, __version__
from genotype.store import api

from .serve import serve_cmd
from .init_cmd import init_cmd
from .load_cmd import load_cmd
from .delete_cmd import delete_cmd
from .match_cmd import match_cmd, check_cmd
from .store_cmd import add_sex, mip_sex, view, ls, sample, export_sample, export_sample_analysis

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-c', '--config', default='~/.genotype.yaml',
              type=click.Path(), help='path to config file')
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO')
@click.option('--log-file', type=click.Path())
@click.version_option(__version__, prog_name=__title__)
@click.pass_context
def root(context, config, database, log_level, log_file):
    """
    Interact with genotype comparison tool.
    """
    coloredlogs.install(level=log_level)

    LOG.debug("%s: version %s", __title__, __version__)

    # read in config file if it exists
    if os.path.exists(config):
        with codecs.open(config) as conf_handle:
            context.obj = yaml.load(conf_handle)
    else:
        context.obj = {}

    context.default_map = context.obj
    if context.obj.get('database') is None:
        context.obj['database'] = database

    if context.invoked_subcommand != 'serve':
        # setup database
        uri = context.obj['database'] or 'sqlite://'
        context.obj['db'] = api.connect(uri)


root.add_command(serve_cmd)
root.add_command(init_cmd)
root.add_command(load_cmd)
root.add_command(delete_cmd)
root.add_command(match_cmd)
root.add_command(check_cmd)
root.add_command(add_sex)
root.add_command(mip_sex)
root.add_command(view)
root.add_command(ls)
root.add_command(sample)
root.add_command(export_sample)
root.add_command(export_sample_analysis)
