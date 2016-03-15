# -*- coding: utf-8 -*-
"""
taboo.cli
~~~~~~~~~
Command line interface (console entry points). Based on Click.
Loads subcommands dynamically using setuptools entry points.
"""
import logging

import click
import yaml

import taboo
import taboo.store
from taboo.subcommands import (delete_cmd, init_cmd, load_cmd, match_cmd,
                               show_cmd, view_cmd)

root_logger = logging.getLogger()


def init_log(log_level=None):
    """Initialize the log file in the proper format.

    Arguments:
        log_level (str): determine level of the log output
    """
    root_logger = logging.getLogger()

    template = "[%(asctime)s] %(levelname)-8s: %(name)-25s: %(message)s"
    formatter = logging.Formatter(template)

    if log_level:
        root_logger.setLevel(getattr(logging, log_level))

    # We will always print warnings and higher to stderr
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root_logger.addHandler(console)


@click.group()
@click.version_option(taboo.__version__)
@click.option('-l', '--log-level', default='INFO')
@click.option('-c', '--config', type=click.Path(exists=True))
@click.option('-d', '--db-uri', type=click.Path())
@click.pass_context
def cli(context, log_level, config, db_uri):
    """Genotype comparison tool."""
    with open(config) as handle:
        options = yaml.load(handle)
        context.obj = options

    db_uri = db_uri or options.get('db_uri') or './taboo.sqlite3'
    init_log(log_level)
    context.obj['store'] = taboo.store.Database(db_uri)


# add subcommands dynamically to the CLI
for subcommand in [delete_cmd, init_cmd, load_cmd, match_cmd, show_cmd,
                   view_cmd]:
    cli.add_command(subcommand)
