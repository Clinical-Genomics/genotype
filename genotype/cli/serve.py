"""Cli command to start the server"""

import logging

import click

from genotype.compat import iteritems
from genotype.server.app import create_app

LOG = logging.getLogger(__name__)


@click.command("serve")
@click.option("--debug", is_flag=True)
@click.option("--port", default=5000)
@click.option("--host", default="localhost")
@click.pass_context
def serve_cmd(context, debug, port, host):
    """Start up the web interface."""
    LOG.info("Running genotype serve")
    flask_config = {
        "GENOTYPE_{}".format(key.upper()): value for key, value in iteritems(context.obj)
    }
    flask_config["SQLALCHEMY_DATABASE_URI"] = context.obj["database"]
    flask_config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app = create_app(config_obj=flask_config)
    app.run(debug=debug, port=port, host=host)
