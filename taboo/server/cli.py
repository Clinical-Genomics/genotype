# -*- coding: utf-8 -*-
import logging

import click

from taboo.compat import iteritems
from taboo.server import create_app

log = logging.getLogger(__name__)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--port', default=5000)
@click.option('--host', default='localhost')
@click.pass_context
def serve(context, debug, port, host):
    """Start up the web interface."""
    flask_config = {"TABOO_{}".format(key.upper()): value for key, value
                    in iteritems(context.obj)}
    flask_config['SQLALCHEMY_DATABASE_URI'] = context.obj['database']
    flask_config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app = create_app('taboo', config_obj=flask_config)
    app.run(debug=debug, port=port, host=host)
