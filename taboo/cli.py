# -*- coding: utf-8 -*-
"""
taboo.cli
~~~~~~~~~
Command line interface (console entry points). Based on Click.
Loads subcommands dynamically using setuptools entry points.
"""
import logging
from pkg_resources import iter_entry_points

import click

import taboo
import taboo.store

root_logger = logging.getLogger()


LEVELS = {
    0: 'WARNING',
    1: 'INFO',
    2: 'DEBUG',
}


def init_log(loglevel=None):
    """Initialize the log file in the proper format.

    Arguments:
        loglevel (str): determine level of the log output
    """
    root_logger = logging.getLogger()

    template = "[%(asctime)s] %(levelname)-8s: %(name)-25s: %(message)s"
    formatter = logging.Formatter(template)

    if loglevel:
        root_logger.setLevel(getattr(logging, loglevel))

    # We will always print warnings and higher to stderr
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root_logger.addHandler(console)


@click.group()
@click.version_option(taboo.__version__)
@click.option('-v', '--verbose', count=True, default=1,
              help="Increase output verbosity. eg. -vv")
@click.option('-d', '--db-path', type=click.Path(), default='./taboo.sqlite3')
@click.pass_context
def cli(context, verbose, db_path):
    """Genotype comparison tool."""
    loglevel = LEVELS.get(min(verbose, 2), 'WARNING')
    init_log(loglevel)
    context.store = taboo.store.Database(db_path)


# add subcommands dynamically to the CLI
for entry_point in iter_entry_points('taboo.subcommand'):
    cli.add_command(entry_point.load())
