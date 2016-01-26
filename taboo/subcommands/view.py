# -*- coding: utf-8 -*-
import click

from taboo.server import flask_app


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--port', default=5000)
@click.pass_context
def view(context, debug, port):
    """View status of the database and samples."""
    flask_app.config.update(context.obj)
    flask_app.run(debug=debug, port=port)
