# -*- coding: utf-8 -*-
"""
genotype.cli
~~~~~~~~~~~
Command line interface (console entry points). Based on Click_.

.. _Click: http://click.pocoo.org/
"""
import codecs
import logging
import os
import pkg_resources

import click
import yaml

from genotype import __title__, __version__
from genotype.log import init_log
from genotype.store import api

log = logging.getLogger(__name__)


class EntryPointsCLI(click.MultiCommand):

    """Add subcommands dynamically to a CLI via entry points."""

    def _iter_commands(self):
        """Iterate over all subcommands as defined by the entry point."""
        return {entry_point.name: entry_point for entry_point in
                pkg_resources.iter_entry_points('genotype.subcommands.2')}

    def list_commands(self, ctx):
        """List the available commands."""
        commands = self._iter_commands()
        return commands.keys()

    def get_command(self, ctx, name):
        """Load one of the available commands."""
        commands = self._iter_commands()
        if name not in commands:
            click.echo("no such command: {}".format(name))
            ctx.abort()
        return commands[name].load()


@click.group(cls=EntryPointsCLI)
@click.option('-c', '--config', default='~/.genotype.yaml',
              type=click.Path(), help='path to config file')
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO')
@click.option('--log-file', type=click.Path())
@click.version_option(__version__, prog_name=__title__)
@click.pass_context
def root(context, config, database, log_level, log_file):
    """Interact with Taboo genotype comparison tool."""
    init_log(logging.getLogger(), loglevel=log_level, filename=log_file)
    log.debug("{}: version {}".format(__title__, __version__))

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
