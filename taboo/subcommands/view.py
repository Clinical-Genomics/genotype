# -*- coding: utf-8 -*-
import click

from taboo.server import flask_app


@click.command()
@click.option('--debug', is_flag=True)
@click.pass_context
def view(context, debug):
    """View status of the database and samples."""
    flask_app.config.update(context.obj)
    flask_app.run(debug=debug)
